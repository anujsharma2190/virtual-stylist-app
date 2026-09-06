import streamlit as st
import google.genai as genai
from PIL import Image
import os
import fal_client

st.set_page_config(page_title="AI Virtual Stylist & Try-On", layout="wide")
st.title("👗 AI Product Recommender & Virtual Try-On")

# Sidebar Keys
st.sidebar.header("Configuration")
gemini_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
fal_key = st.sidebar.text_input("Enter FAL API Key", type="password")

col1, col2 = st.columns(2)

with col1:
    uploaded_user = st.file_uploader("1. Upload Your Photo", type=["jpg", "png", "jpeg"])
    if uploaded_user:
        st.image(uploaded_user, caption="User Photo", width=250)

with col2:
    uploaded_item = st.file_uploader("2. Upload Clothing Item Photo", type=["jpg", "png", "jpeg"])
    if uploaded_item:
        st.image(uploaded_item, caption="Garment Photo", width=250)

style_preference = st.selectbox("Style Preference", ["Casual Chic", "Formal / Business", "Party Wear", "Streetwear", "Traditional / Ethnic"])
budget = st.text_input("Budget & Occasion", "Under $100 for a weekend brunch")

if st.button("Generate Recommendation & Try-On", type="primary"):
    if not gemini_key or not fal_key:
        st.error("Please enter both Gemini and FAL API Keys in the sidebar.")
    elif not uploaded_user or not uploaded_item:
        st.error("Please upload both a user photo and a garment photo for image-to-image try-on.")
    else:
        os.environ["FAL_KEY"] = fal_key
        
        with st.spinner("Analyzing style and rendering exact try-on..."):
            try:
                # 1. Get Stylist Text Recommendation from Gemini
                client = genai.Client(api_key=gemini_key)
                user_img = Image.open(uploaded_user)
                item_img = Image.open(uploaded_item)
                
                prompt = f"""
                Act as an expert personal fashion stylist. 
                Analyze the user photo and garment photo.
                Style Preference: {style_preference}
                Budget/Occasion: {budget}
                
                Explain why this garment suits the user's features and offer styling advice.
                """
                
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[user_img, item_img, prompt]
                )
                
                st.subheader("💡 Stylist Advice")
                st.write(response.text)

                # 2. Upload images to FAL temporarily and call IDM-VTON
                user_url = fal_client.upload_file(uploaded_user.getvalue(), "image/jpeg")
                garment_url = fal_client.upload_file(uploaded_item.getvalue(), "image/jpeg")

                result = fal_client.subscribe(
                    "fal-ai/idm-vton",
                    arguments={
                        "human_image_url": user_url,
                        "garment_image_url": garment_url,
                        "description": style_preference
                    }
                )

                # 3. Display the Output Image
                st.subheader("🖼️ Virtual Try-On Render")
                output_image_url = result["image"]["url"]
                st.image(output_image_url, caption="Virtual Try-On Result", use_container_width=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
