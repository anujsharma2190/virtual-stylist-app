import streamlit as st
import google.genai as genai
from PIL import Image
import urllib.parse

# Page Configuration
st.set_page_config(page_title="AI Virtual Stylist & Try-On", layout="wide")
st.title("👗 AI Product Recommender & Virtual Try-On")
st.caption("Upload your photo, set your budget and style, and get custom recommendations with visual try-ons.")

# Sidebar for API Configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# Main Inputs
col1, col2 = st.columns(2)

with col1:
    uploaded_user = st.file_uploader("1. Upload Your Photo (User/Model)", type=["jpg", "png", "jpeg"])
    if uploaded_user:
        st.image(uploaded_user, caption="User Photo", width=250)

with col2:
    uploaded_item = st.file_uploader("2. Optional: Upload Clothing/Product Image", type=["jpg", "png", "jpeg"])
    if uploaded_item:
        st.image(uploaded_item, caption="Target Product", width=250)

style_preference = st.selectbox("Style Preference", ["Casual Chic", "Formal / Business", "Party Wear", "Streetwear", "Traditional / Ethnic"])
budget = st.text_input("Budget & Occasion", "Under $100 for a weekend brunch")

if st.button("Generate Recommendation & Try-On", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not uploaded_user:
        st.error("Please upload a user photo to proceed.")
    else:
        with st.spinner("AI is analyzing style and creating recommendations..."):
            try:
                # Initialize Gemini Client
                client = genai.Client(api_key=api_key)
                user_img = Image.open(uploaded_user)
                
                prompt = f"""
                Act as an expert personal fashion stylist. 
                Analyze the uploaded user photo (body tone, silhouette, hair) and style preferences.
                Preference: {style_preference}
                Budget/Occasion: {budget}
                
                Provide your response in 2 distinct sections:
                
                SECTION 1: RECOMMENDATIONS
                - Give 3 specific item recommendations that complement this user.
                - Explain WHY these items work well for them.
                
                SECTION 2: TRY-ON PROMPT
                - Write ONE highly detailed, photorealistic image description of the user wearing the top recommended outfit.
                - Format it exactly like this: TRYON_PROMPT: <a high-resolution photorealistic image description of a model wearing [outfit details]>
                """

                inputs = [user_img, prompt]
                if uploaded_item:
                    item_img = Image.open(uploaded_item)
                    inputs.append(item_img)

                # Call Gemini API
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=inputs
                )
                
                full_text = response.text
                
                # Display Text Recommendations
                st.subheader("💡 Stylist Recommendations")
                st.write(full_text.split("SECTION 2:")[0].replace("SECTION 1:", ""))

                # Extract Prompt & Render Virtual Try-On Image
                if "TRYON_PROMPT:" in full_text:
                    raw_prompt = full_text.split("TRYON_PROMPT:")[1].strip()
                    encoded_prompt = urllib.parse.quote(raw_prompt)
                    
                    # Generate Image via Pollinations free API
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true&seed=42"
                    
                    st.subheader("🖼️ Virtual Try-On Render")
                    st.image(image_url, caption="AI Generated Virtual Try-On Preview", use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
