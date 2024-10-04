import streamlit as st
import difflib 
from openai import OpenAI 
from pydantic import BaseModel



def highlight_corrections(original,corrected):
    """
    Highlights the differences between original user message and corrected message.

    args:
        original (str): original user message
        corrected (str): corrected form provided by LLM

    returns:
        tuple containing two strings:
        - original user message with mistakes highlighted in red
        - corrected form with added corrections highlighted in green
    """

    if " " in corrected: #decide granularity of difference calculation
        #word-based difference calculation
        original = original.split()
        corrected = corrected.split()
        separator = " "
    else:
        #character-based difference calculation (beneficial for one-word inputs and languages that do not use spaces in writing)
        separator = ""  

    #returns generator of the differences between original user message and corrected form
    differences = difflib.ndiff(original, corrected)
    
    #lists for highlighted results
    result_original = []
    result_corrected = []

    for line in differences:
        if line.startswith('  '): #no difference
            result_original.append(line[2:])
            result_corrected.append(line[2:])
        elif line.startswith('- '): #absent in corrected form -> mistake in original user message 
            result_original.append(f':red-background[{line[2:]}]') #add mistake to resulting user message
        elif line.startswith('+ '): #absent in user message -> added correction in corrected form
            result_corrected.append(f':green-background[{line[2:]}]') #add correction to resulting corrected form

    #join the lists with seperator to create strings
    return separator.join(result_original),separator.join(result_corrected)

#streamlit sidebar
st.sidebar.title("Customization Options")
#language level settings
st.sidebar.subheader("Language Level")
select_proficiency = st.sidebar.selectbox(
    "Select language level (CEFR) of the chatbot.",
    ("A1", "A2", "B1", "B2", "C1", "C2"),
    index=None,
    placeholder="Select proficiency level...",
)
#visible explanation for default setting
st.sidebar.markdown("If nothing is selected, the chatbot will try to adapt to **your** language level.")

#string interpolation to system message based on value of select_proficiency
if select_proficiency is None:
    language_level = "Adapt your language level to the language level of the user."
else:
    language_level = f"Adapt your language level to CEFR {select_proficiency}."

st.sidebar.subheader("Tips")
st.sidebar.markdown("💡 You can customize the chatbot on your own by stating *Your name is Alice, you work as a space engineer, and you love telling jokes.* in your first message.")
st.sidebar.markdown("💭 If you run out of ideas on what to talk about, just ask the chatbot directly: *What do you want to talk about?* or *What did you do last weekend?*")
st.sidebar.markdown("🔃 You can reset the conversation by refreshing the site.")


st.title("Language Exchange Partner") 

client = OpenAI(api_key="<INSERT API KEY HERE>") #pass OpenAI API key

#define data structure for "Structured Output"
class Response(BaseModel):
    reply: str #chatbot reply to user message
    corrected_form: str #corrected form of user message

#contains all user messages and non-formatted assistant messages, used to send back to API
if "conversation_raw" not in st.session_state:
    st.session_state.conversation_raw = []
    
#contains all user messages and formatted assistant messages, used to display conversation history
if "conversation_shown" not in st.session_state:
    st.session_state.conversation_shown = []

#display conversation history (all previous messages)
for message in st.session_state.conversation_shown:
    st.chat_message(message["role"]).markdown(message["content"])


#input of user message starts flow that triggers response generation from LLM
if user_message := st.chat_input("Type a message..."):

    #store user message in conversation histories and display user message
    st.session_state.conversation_raw.append({"role": "user", "content": user_message})
    st.session_state.conversation_shown.append({"role": "user", "content": user_message})
    st.chat_message("user").markdown(user_message)

    
    #system prompt contains fundamental instructions to LLM
    system_message = {
        "role": "system",
        "content": f"The user practices English by chatting with you, a native speaker.\n\n You have two tasks:\n\n Task 1) Reply as if you were a human chat partner, not a GPT assistant. Create a fictional identity for yourself. Your replies are short. {language_level}\n\n Task 2) If the current user message contains linguistic mistakes, provide a corrected form of the current user message."}

    #generate response from LLM
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06", #latest model available at the time of implementation, supports "Structured Output"
        messages=[system_message] + st.session_state.conversation_raw, #provide entire chat history to preserve context of conversation
        response_format=Response, #forces model to produce output that adheres to previously defined data structure "Response"
    )

    #retrieve response as an object of type "Response"
    response = completion.choices[0].message.parsed 

    if response is not None: #check if transmission was successful   
        if response.corrected_form.strip() == "" or response.corrected_form.strip() == user_message.strip(): #compare corrected_form of assistant message to user message
            #no errors detected, no corrections made by LLM
            response.corrected_form = "" #delete unused corrected_form to reduce input tokens
        
        else: 
            #corrections were made by LLM
            incorrect, correct = highlight_corrections(user_message,response.corrected_form) #generate highlighted strings
            correction_message = incorrect + "\n\n" + correct #combine original user message (errors highlighted in red) with corrected form (corrections highlighted in green)
            st.chat_message("✏️").markdown(correction_message) #display feedback message
            st.session_state.conversation_shown.append({"role": "✏️", "content": correction_message}) #add feedback message to conversation history (formatted)

        st.session_state.conversation_raw.append({"role": "assistant", "content": str(response)}) #add assistant message to conversation history (raw)
    
        st.chat_message("assistant").markdown(response.reply) #display reply of assistant message
        st.session_state.conversation_shown.append({"role": "assistant", "content": response.reply}) #add reply of assistant message to conversation history (formatted)
      

    else: #no Response from LLM due to transmission problem
        st.error('Your message could not be transmitted. Please send it again.', icon="🚨")
        st.session_state.conversation_raw.pop() #remove user message from conversation history (raw) to not include in next request
        st.session_state.conversation_shown[-1]['content'] = f":red[{st.session_state.conversation_shown[-1]['content']}]"#mark unsubmitted user message in red to give visual aid 