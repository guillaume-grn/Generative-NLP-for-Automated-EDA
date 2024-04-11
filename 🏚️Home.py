import streamlit as st

st.set_page_config(
    page_title="EDA",
    page_icon="📊",
)

st.write("# 📊 SQL Data Analysis powered by LLM ")

uploaded_file = st.file_uploader("Download the SQL file", type=[".sqlite", ".db"])
if uploaded_file is not None :
    st.session_state['uploaded_file'] = uploaded_file
    #write the file at the root of the app
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

if 'uploaded_file' in st.session_state :
    db_name=st.session_state['uploaded_file'].name

    st.write("You uploaded:", db_name)

# st.markdown(
#     """
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     - Jump into our [documentation](https://docs.streamlit.io)
#     - Ask a question in our [community
#         forums](https://discuss.streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )