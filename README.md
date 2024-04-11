# Generative NLP for Automated EDA

## Installation :
- Clone the repo
- Create a env.py file with the  following lines :
    '''
    OPEN_AI_KEY="xxx"
    MISTRAL_API_KEY='xxx'
    AWS_ACCESS_KEY_ID='xxx'
    AWS_SECRET_ACCESS_KEY='xxx'
    '''
- Make sure to have the required packages installed (langchain, streamlit, dotenv, boto3)

## Running the Streamlit App :
- Run the following command in your terminal: 'streamlit run ./🏚️Home.py'
- You can increase the 200MB upload limit for your database file adding the argument: '--server.maxUploadSize 500 '
