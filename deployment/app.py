import streamlit as st
from taskflowai import Task, set_verbosity
import re
from src.agentic.agents.reporter_agent import TravelReportAgent
from src.agentic.agents.travel_agent import TravelAgent
from src.agentic.agents.web_research_agent import WebResearchAgent
from src.agentic.logger import logging
from src.agentic.exception import CustomException

# Config
st.set_page_config(
    page_title="TRIPSAGE: Your Travel Planning Begins Here!",
    layout="wide",
    initial_sidebar_state="collapsed"
)
set_verbosity(True)

# CSS
st.markdown("""
    <style>
    .block-container { padding: 1rem; max-width: 960px; margin: 0 auto; }
    .section-header { margin: 1.5rem 0 1rem; padding: 0.5rem; background-color: #1e3a8a; color: white; border-radius: 0.3rem; }
    .content-section { padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1.5rem; border: 1px solid #e5e7eb; background-color: #1e293b; color: white; }
    .stTextInput { margin-bottom: 0.5rem; }
    .stButton button { margin: 1rem 0; }
    .stSuccess, .stError, .stWarning { padding: 0.75rem; border-radius: 0.3rem; margin: 1rem 0; }
    </style>
    """, unsafe_allow_html=True)

# Agents
reporter_agent = TravelReportAgent.initialize_travel_report_agent()
travel_agent = TravelAgent.initialize_travel_agent()
web_research_agent = WebResearchAgent.initialize_web_research_agent()

# Format image markdown
def format_markdown_images(markdown_text):
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    def fix_url(match):
        alt_text, url = match.groups()
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = f"https:{url}" if url.startswith('//') else f"https://{url}"
        return f'![{alt_text}]({url})'
    return re.sub(img_pattern, fix_url, markdown_text)

# Core functions
def research_destination(destination, interests):
    instruction = (
        f"Create a comprehensive report about {destination} with the following:\n"
        f"1. Include 2-3 high-quality images of key attractions using valid image markdown format: ![Alt Text](https://full-image-url)\n"
        f"2. Ensure image URLs are complete and start with https:// or http://\n"
        f"3. Add a short caption/description below each image\n"
        f"4. Cover top attractions and activities relevant to: {interests}\n"
        f"5. Format the whole response in clean markdown sections with proper headers."
    )
    return Task.create(agent=web_research_agent, context=f"{destination}, {interests}", instruction=instruction)


def research_events(destination, dates, interests):
    instruction = (
        f"List events in {destination} during {dates} matching interests: {interests}, with image markdown and short descriptions."
    )
    return Task.create(agent=web_research_agent, context=f"{destination}, {dates}, {interests}", instruction=instruction)

def research_weather(destination, dates):
    instruction = (
        "Provide weather forecast including temp range, rain chances, and packing tips."
    )
    return Task.create(agent=travel_agent, context=f"{destination}, {dates}", instruction=instruction)

def search_flights(current_location, destination, dates):
    instruction = (
        "Find top 3 affordable flights from source to destination with bullet points and prices in INR (₹), include airline, departure time, duration, and total price."
    )
    return Task.create(agent=travel_agent, context=f"From {current_location} to {destination}, Dates: {dates}", instruction=instruction)

def search_hotels(destination, dates, budget_inr):
    budget_usd = round(float(budget_inr) / 83, 2)  # Convert INR to USD for backend logic
    instruction = (
        f"List 3 hotel stays in {destination} within a total budget of ₹{budget_inr} (~${budget_usd}) for the trip dates {dates}. "
        f"Include name, location, star rating, price in INR, and image markdown if possible."
    )
    return Task.create(agent=travel_agent, context=f"{destination}, {dates}, budget: ₹{budget_inr}", instruction=instruction)

def write_travel_report(destination_report, events_report, weather_report, flight_report, hotel_report):
    instruction = (
        "Create a travel itinerary using all sections (destination, events, weather, flights, hotels) in markdown. "
        "Preserve image markdown and captions. Format clearly with headers and sections."
    )
    context = (
        f"Destination Report:\n{destination_report}\n\n"
        f"Events Report:\n{events_report}\n\n"
        f"Weather Report:\n{weather_report}\n\n"
        f"Flight Report:\n{flight_report}\n\n"
        f"Hotel Report:\n{hotel_report}"
    )
    return Task.create(agent=reporter_agent, context=context, instruction=instruction)

# UI
def main():
    st.title("TRIPSAGE: Your Travel Planning Begins Here!")
    with st.container():
        st.subheader("📝 Enter Trip Details")

        col1, col2 = st.columns(2)
        with col1:
            current_location = st.text_input("Departure City", placeholder="e.g., Mumbai")
            destination = st.text_input("Destination City", placeholder="e.g., Paris")
        with col2:
            dates = st.text_input("Travel Dates", placeholder="Dec 20-25, 2024")
            interests = st.text_input("Your Interests", placeholder="e.g., museums, food, hiking")
        budget = st.text_input("Your Budget (in INR)", placeholder="e.g., 80000")

    plan_button = st.button("Create My Travel Itinerary 🚀", type="primary", use_container_width=True)

    if plan_button:
        if current_location and destination and dates and budget:
            try:
                st.success("🎈 Sit tight! Preparing your travel planning journey!")
                st.balloons()

                sections = {
                    "destination": ("📍 Destination Information", research_destination),
                    "events": ("🎯 Events & Activities", research_events),
                    "weather": ("☀️ Weather Forecast", research_weather),
                    "flights": ("✈️ Flight Options", search_flights),
                    "hotels": ("🏨 Hotel Recommendations", search_hotels)
                }

                reports = {}

                for key, (title, func) in sections.items():
                    with st.container():
                        st.markdown(f"<div class='section-header'><h3>{title}</h3></div>", unsafe_allow_html=True)
                        with st.spinner(f"Loading {title.lower()}..."):
                            if key == "destination":
                                reports[key] = func(destination, interests)
                            elif key == "events":
                                reports[key] = func(destination, dates, interests)
                            elif key == "weather":
                                reports[key] = func(destination, dates)
                            elif key == "flights":
                                reports[key] = func(current_location, destination, dates)
                            elif key == "hotels":
                                reports[key] = func(destination, dates, budget)

                            try:
                                st.markdown(format_markdown_images(reports[key]))
                            except Exception as e:
                                st.error(f"Error displaying {key} section: {str(e)}")
                                st.markdown(reports[key])

                st.markdown("<div class='section-header'><h3>📋 Here's your Complete Travel Plan</h3></div>", unsafe_allow_html=True)
                with st.spinner("Creating final report..."):
                    final_report = write_travel_report(
                        reports["destination"],
                        reports["events"],
                        reports["weather"],
                        reports["flights"],
                        reports["hotels"]
                    )
                    try:
                        st.markdown(format_markdown_images(final_report))
                    except Exception as e:
                        st.error(f"Error displaying final report: {str(e)}")
                        st.markdown(final_report)

                st.download_button(
                    label="📥 Download your itinerary",
                    data=final_report,
                    file_name=f"travel_plan_{destination.lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"🚨 An error occurred: {str(e)}")
        else:
            st.warning("🔔 Please fill in all required fields, including your budget!")

    st.markdown("<p style='text-align: center; color: #FFFFFF; margin-top: 2rem;'>Happy Travelling 🌟 - Team A13</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()



# import streamlit as st
# from taskflowai import  Task, set_verbosity
# import os
# import re
# from src.agentic.agents.reporter_agent import TravelReportAgent
# from src.agentic.agents.travel_agent import TravelAgent
# from src.agentic.agents.web_research_agent  import WebResearchAgent
# from src.agentic.logger import logging
# from src.agentic.exception import CustomException

# # Must be the first Streamlit command
# st.set_page_config(
#     page_title="TRIPSAGE: Your Travel Planning Begins Here!",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # Set verbosity for debugging purposes
# set_verbosity(True)

# # Load environment variables

# # First, simplify the CSS by removing the white backgrounds and fixing contrast
# st.markdown("""
#     <style>
#     /* Container styling */
#     .block-container {
#         padding: 1rem;
#         max-width: 960px;
#         margin: 0 auto;
#     }
    
#     /* Section styling */
#     .section-header {
#         margin: 1.5rem 0 1rem;
#         padding: 0.5rem;
#         background-color: #1e3a8a;
#         color: white;
#         border-radius: 0.3rem;
#     }
    
#     /* Content sections */
#     .content-section {
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         margin-bottom: 1.5rem;
#         border: 1px solid #e5e7eb;
#         background-color: #1e293b;
#         color: white;
#     }
    
#     /* Form styling */
#     .stTextInput {
#         margin-bottom: 0.5rem;
#     }
    
#     /* Button styling */
#     .stButton button {
#         margin: 1rem 0;
#     }
    
#     /* Message styling */
#     .stSuccess, .stError, .stWarning {
#         padding: 0.75rem;
#         border-radius: 0.3rem;
#         margin: 1rem 0;
#     }
#     </style>
#     """, unsafe_allow_html=True)


# # Define agents
# reporter_agent = TravelReportAgent.initialize_travel_report_agent()
# travel_agent= TravelAgent.initialize_travel_agent()
# web_research_agent  = WebResearchAgent.initialize_web_research_agent()

# # Then, simplify the image formatting function to preserve markdown
# def format_markdown_images(markdown_text):
#     """
#     Keep markdown image syntax intact and just ensure URLs are properly formatted
#     """
#     import re
    
#     # Only process markdown images without converting to HTML
#     img_pattern = r'!\[(.*?)\]\((.*?)\)'
    
#     def fix_url(match):
#         alt_text, url = match.groups()
#         url = url.strip()
#         if not url.startswith(('http://', 'https://')):
#             url = f"https:{url}" if url.startswith('//') else f"https://{url}"
#         return f'![{alt_text}]({url})'
    
#     return re.sub(img_pattern, fix_url, markdown_text)
 


# def research_destination(destination, interests):
#     """Research destination with enhanced image handling"""
#     instruction = (
#         f"Create a comprehensive report about {destination} with the following:\n"
#         f"1. Use Wikipedia tools to find and include 2-3 high-quality images of key attractions\n"
#         f"2. Ensure images are full URLs starting with http:// or https://\n"
#         f"3. Format images as: ![Description](https://full-image-url)\n"
#         f"4. Include a brief caption for each image\n"
#         f"5. Research attractions and activities related to: {interests}\n"
#         f"6. Organize the report with proper headings and sections\n"
#         f"7. Place images naturally throughout the content where relevant\n"
#         f"8. Include practical visitor information\n"
#         f"Format the entire response in clean markdown"
#     )
#     try:
#         task = Task.create(
#             agent=web_research_agent,
#             context=f"User Destination: {destination}\nUser Interests: {interests}",
#             instruction=instruction
#         )
#         logging.info("Successfully created destination research task.")
#         return task
#     except Exception as e:
#         logging.info(f"Failed to create destination research task: {str(e)}")
#         raise CustomException(f"Error creating destination research task: {str(e)}")


# def research_events(destination, dates, interests):
#     """Research events with enhanced image handling"""
#     instruction = (
#         f"Research events in {destination} during {dates} that match these interests: {interests}.\n\n"
#         f"For each event, include:\n"
#         f"- Event name\n"
#         f"- Date and time\n"
#         f"- Venue/location\n"
#         f"- Ticket information (if applicable)\n"
#         f"- A short description of the event\n"
#         f"- Format event images as: ![Event Name](https://full-image-url)\n"
#         f"- Format images as: ![Description](https://full-image-url)\n"
#         f"- Ensure images are full URLs starting with http:// or https://\n"
#         f"- Information is accurate and up-to-date\n"
#         f"- Place images naturally throughout the content where relevant\n"
#         f"- Format the entire response in clean markdown"
#     )
#     try:
#         task = Task.create(
#             agent=web_research_agent,
#             context=f"Destination: {destination}\nDates: {dates}\nInterests: {interests}",
#             instruction=instruction
#         )
#         logging.info("Successfully created events research task.")
#         return task
#     except Exception as e:
#         logging.info(f"Failed to create events research task: {str(e)}")
#         raise CustomException(f"Error creating events research task: {str(e)}")


# def research_weather(destination, dates):
#     """Research weather information"""
#     try:
#         task = Task.create(
#             agent=travel_agent,
#             context=f"Destination: {destination}\nDates: {dates}",
#             instruction=(
#                 "Provide detailed weather information including:\n"
#                 "1. Temperature ranges\n"
#                 "2. Precipitation chances\n"
#                 "3. General weather patterns\n"
#                 "4. Recommended clothing/gear"
#             )
#         )
#         logging.info("Successfully created weather research task.")
#         return task
#     except Exception as e:
#         logging.info(f"Failed to create weather research task: {str(e)}")
#         raise CustomException(f"Error creating weather research task: {str(e)}")


# def search_flights(current_location, destination, dates):
#     """Search flight options"""
#     try:
#         task = Task.create(
#             agent=travel_agent,
#             context=f"Flights from {current_location} to {destination} on {dates}",
#             instruction="Find top 3 affordable and convenient flight options and provide concise bullet-point information"
#         )
#         logging.info("Successfully created flight search task.")
#         return task
#     except Exception as e:
#         logging.info(f"Failed to create flight search task: {str(e)}")
#         raise CustomException(f"Error creating flight search task: {str(e)}")


# def write_travel_report(destination_report, events_report, weather_report, flight_report):
#     """Create final travel report"""
#     try:
#         task = Task.create(
#             agent=reporter_agent,
#             context=f"Destination Report: {destination_report}\n\n"
#                     f"Events Report: {events_report}\n\n"
#                     f"Weather Report: {weather_report}\n\n"
#                     f"Flight Report: {flight_report}",
#             instruction=(
#                 "Create a comprehensive travel report that:\n"
#                 "1. Maintains all images from the destination and events reports\n"
#                 "2. Organizes information in a clear, logical structure\n"
#                 "3. Keeps all markdown formatting intact\n"
#                 "4. Ensures images are properly displayed with captions\n"
#                 "5. Includes all key information from each section"
#             )
#         )
#         logging.info("Successfully created travel report.")
#         return task
#     except Exception as e:
#         logging.info(f"Failed to create travel report: {str(e)}")
#         raise CustomException(f"Error creating travel report: {str(e)}")

# def main():
#     st.title("TRIPSAGE: Your Travel Planning Begins Here!")
    
#     with st.container():
#         st.subheader("📝 Enter Trip Details")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             current_location = st.text_input(
#                 "Departure City",
#                 placeholder="Enter your starting point"
#             )
#             destination = st.text_input(
#                 "Destination City",
#                 placeholder="Enter your destination"
#             )
            
#         with col2:
#             dates = st.text_input(
#                 "Travel Dates",
#                 placeholder="Dec 20-25, 2024"
#             )
#             interests = st.text_input(
#                 "Your Interests",
#                 placeholder="museums, food, hiking..."
#             )

#     plan_button = st.button("Create My Travel Itinerary 🚀", type="primary", use_container_width=True)

#     if plan_button:
#         if current_location and destination and dates:
#             try:
#                 st.success("🎈 Sit tight! Preparing your travel planning journey!")
#                 st.balloons()

#                 sections = {
#                     "destination": ("📍 Destination Information", research_destination),
#                     "events": ("🎯 Events & Activities", research_events),
#                     "weather": ("☀️ Weather Forecast", research_weather),
#                     "flights": ("✈️ Flight Options", search_flights)
#                 }

#                 reports = {}

#                 for key, (title, func) in sections.items():
#                     with st.container():
#                         st.markdown(f"<div class='section-header'><h3>{title}</h3></div>", 
#                                   unsafe_allow_html=True)
#                         with st.spinner(f"Loading {title.lower()}..."):
#                             if key == "destination":
#                                 reports[key] = func(destination, interests)
#                             elif key == "events":
#                                 reports[key] = func(destination, dates, interests)
#                             elif key == "weather":
#                                 reports[key] = func(destination, dates)
#                             else:  # flights
#                                 reports[key] = func(current_location, destination, dates)
                            
#                             try:
#                                 formatted_content = format_markdown_images(reports[key])
#                                 st.markdown(formatted_content)  # Just use regular markdown
#                             except Exception as e:
#                                 st.error(f"Error displaying content: {str(e)}")
#                                 st.markdown(reports[key])

#                 st.markdown("<div class='section-header'><h3>📋 Here's your Complete Travel Plan</h3></div>", 
#                           unsafe_allow_html=True)
#                 with st.spinner("Creating final report..."):
#                     final_report = write_travel_report(
#                         reports["destination"],
#                         reports["events"],
#                         reports["weather"],
#                         reports["flights"]
#                     )
#                     # And for the final report:
#                     try:
#                         formatted_final_report = format_markdown_images(final_report)
#                         st.markdown(formatted_final_report)  # Just use regular markdown
#                     except Exception as e:
#                         st.error(f"Error displaying final report: {str(e)}")
#                         st.markdown(final_report)
                
#                 st.download_button(
#                     label="📥 Download your itinerary",
#                     data=final_report,
#                     file_name=f"travel_plan_{destination.lower().replace(' ', '_')}.md",
#                     mime="text/markdown",
#                     use_container_width=True
#                 )

#             except Exception as e:
#                 st.error(f"🚨 An error occurred: {str(e)}")
#                 print(f"Debug - Error details: {str(e)}")
#         else:
#             st.warning("🔔 Please fill in all required fields")

#     st.markdown("""
#         <p style='text-align: center; color: #FFFFFF; margin-top: 2rem;'>
#             Happy Travelling 🌟- Team A13
#         </p>
#         """, unsafe_allow_html=True)

# if __name__ == "__main__":
#     main()