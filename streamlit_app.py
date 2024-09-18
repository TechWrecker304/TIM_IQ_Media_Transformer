import streamlit as st
import openai
from newspaper import Article
from urllib.parse import urlparse
import html
import base64
from PIL import Image
import io

# Constants
APP_NAME = "Trust In Media (TIM) Media Transformer"
BACKGROUND_COLOR = "#F0F4F8"
TEXT_COLOR = "#2C3E50"
HIGHLIGHT_COLOR = "#3498DB"
BUTTON_BG = "#2980B9"
BUTTON_FG = "white"
ENTRY_BG = "white"

# Media outlets
MEDIA_OUTLETS = [
    "New York Times", "New York Post", "Washington Post", "Washington Times",
    "Breitbart", "Daily Beast", "Fox News", "CNN", "AP", "Bloomberg",
    "Huffpost", "The Blaze", "Mother Jones", "Vox", "Politico",
    "The Daily Wire", "Epoch Times", "Newsmax", "National Review", "Axios",
    "BBC", "The Guardian", "Wall Street Journal", "NPR", "Reuters"
]

def gpt4_interaction(prompt, max_tokens=1500):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a media transformation assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error interacting with OpenAI: {e}")
        return None

def transform_media(input_text, outlet):
    original_text = get_text_from_input(input_text)

    prompt = f"""Transform the following text to match the style, tone, political leaning, and overall perspective of {outlet}. Consider the following:

1. Political bias: Adjust the article's stance to align with {outlet}'s known political leanings (e.g., conservative, liberal, centrist).
2. Topic emphasis: Highlight or downplay certain aspects of the story based on what {outlet} typically focuses on.
3. Language and tone: Use vocabulary, phrasing, and tone that are characteristic of {outlet}'s writing style.
4. Source selection: If applicable, change or add quotes from sources that {outlet} would likely feature.
5. Headline style: Create a new headline in the style of {outlet}.

Original text:
{original_text}

Provide the transformed text, including a new headline, followed by a brief analysis of the changes made. Separate the transformed text and analysis with three dashes (---) on a new line."""

    response = gpt4_interaction(prompt)
    if response:
        parts = response.split("\n---\n")
        if len(parts) == 2:
            transformed_text, analysis = parts
        else:
            transformed_text = parts[0]
            analysis = "No separate analysis provided."
        return original_text, transformed_text.strip(), analysis.strip()
    else:
        st.error("There was an issue processing the text with the OpenAI API.")
        return None, None, None

def get_text_from_input(input_text):
    if is_url(input_text):
        try:
            article = Article(input_text)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            st.error(f"Failed to fetch article from URL: {str(e)}")
            return None
    else:
        return input_text

def is_url(text):
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def simulate_social_media_posts(original_text, transformed_text, outlet):
    prompt = f"""Based on the following original article and its transformed version from {outlet}, create simulated social media posts for X (Twitter), Facebook, Instagram, and TikTok. Each post should reflect the style and tone of the respective platform. Provide one post for each platform for both the original and transformed versions.

Original article:
{original_text}

Transformed article ({outlet}):
{transformed_text}

Format your response as follows:
Original Article Posts:
X (Twitter):
[Simulated X post]

Facebook:
[Simulated Facebook post]

Instagram:
[Simulated Instagram post]

TikTok:
[Simulated TikTok post description]

Transformed Article Posts ({outlet}):
X (Twitter):
[Simulated X post]

Facebook:
[Simulated Facebook post]

Instagram:
[Simulated Instagram post]

TikTok:
[Simulated TikTok post description]
"""

    response = gpt4_interaction(prompt)
    return response

def generate_html_report(original_text, transformed_text, analysis, outlet):
    return f"""
    <html>
    <head>
        <title>{APP_NAME} - {outlet} Transformation Report</title>
        <style>
            body {{font-family: Arial, sans-serif; padding: 20px; background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; line-height: 1.6;}}
            h1 {{color: {HIGHLIGHT_COLOR}; text-align: center;}}
            h2 {{color: {TEXT_COLOR}; margin-top: 40px;}}
            .container {{display: flex; justify-content: space-between; margin-top: 20px;}}
            .text-box {{width: 48%; padding: 15px; background-color: {ENTRY_BG}; border: 1px solid #ddd; border-radius: 8px;}}
            pre {{font-size: 14px; white-space: pre-wrap; word-wrap: break-word;}}
            .original {{background-color: #eef4ff;}}
            .transformed {{background-color: #e8f3ea;}}
            .analysis {{margin-top: 20px; padding: 15px; background-color: #fff3cd; border-radius: 8px; color: #856404;}}
        </style>
    </head>
    <body>
        <h1>{outlet} Transformation Report</h1>
        <div class="container">
            <div class="text-box original">
                <h2>Original Text</h2>
                <pre>{html.escape(original_text)}</pre>
            </div>
            <div class="text-box transformed">
                <h2>{outlet} Style</h2>
                <pre>{html.escape(transformed_text)}</pre>
            </div>
        </div>
        <div class="analysis">
            <h2>Transformation Analysis</h2>
            <pre>{html.escape(analysis)}</pre>
        </div>
    </body>
    </html>
    """

def main():
    st.set_page_config(page_title=APP_NAME, page_icon="🗞️", layout="wide")

    # Load and display logo
    logo_img = Image.open("./tim_logo.png")
    logo_img = logo_img.resize((200, 100))
    st.image(logo_img, use_column_width=False)

    st.title(APP_NAME)

    # API Key input
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if api_key:
        openai.api_key = api_key
    else:
        st.warning("Please enter your OpenAI API Key to use the app.")
        return

    # Input area
    input_text = st.text_area("Enter article text or URL:", height=200)

    # Media outlet selection
    outlet = st.selectbox("Select media outlet:", MEDIA_OUTLETS)

    if st.button("Transform"):
        if not input_text:
            st.warning("Please paste an article or URL into the text area.")
        else:
            with st.spinner("Processing..."):
                original_text, transformed_text, analysis = transform_media(input_text, outlet)

            if original_text and transformed_text and analysis:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Original Text")
                    st.text_area("", value=original_text, height=400, disabled=True)
                with col2:
                    st.subheader(f"{outlet} Style")
                    st.text_area("", value=transformed_text, height=400, disabled=True)

                st.subheader("Transformation Analysis")
                st.text_area("", value=analysis, height=200, disabled=True)

                # HTML Report
                html_report = generate_html_report(original_text, transformed_text, analysis, outlet)
                st.download_button(
                    label="Save Report as HTML",
                    data=html_report,
                    file_name="transformation_report.html",
                    mime="text/html"
                )

                # Simulate Social Media Posts
                if st.button("Simulate Social Media Posts"):
                    with st.spinner("Generating social media posts..."):
                        social_media_posts = simulate_social_media_posts(original_text, transformed_text, outlet)
                    
                    if social_media_posts:
                        st.subheader("Simulated Social Media Posts")
                        st.text_area("", value=social_media_posts, height=400, disabled=True)
                        
                        # Download button for social media posts
                        st.download_button(
                            label="Save Posts as Text",
                            data=social_media_posts,
                            file_name="simulated_social_media_posts.txt",
                            mime="text/plain"
                        )

if __name__ == "__main__":
    main()