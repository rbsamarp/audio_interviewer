import openai
import streamlit as st
from dotenv import load_dotenv
import json
import os
import pyttsx3  # For Text-to-Speech conversion
import uuid  # For generating unique IDs


# Load environment variables from .env file
load_dotenv()


# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()

# Load OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# File path to store user data
DATA_FILE = "user_data.json"
DEFAULT_JD = """Our program offers interns a unique dual experience. Interns will be placed in a specific department, but will also have the opportunity to work on cross-functional projects. This will allow interns to gain a broad understanding of our business and the industry as a whole. Interns will be assigned a mentor who will provide guidance and support throughout the program. At the end of the internship, interns will have the opportunity to present their work to senior leaders. We are looking for candidates who are passionate, eager to learn, and ready to make an impact. 
Programming Languages: Mid level Proficiency in programming languages is fundamental. Common languages include Java, Python, C++, and JavaScript. These languages are used for various applications, from web development to software engineering.
Data Structures and Algorithms: Understanding data structures (like arrays, linked lists, stacks, and queues) and algorithms (such as sorting and searching) is crucial for problem-solving and efficient coding.
Software Development: Knowledge of the software development lifecycle, including methodologies like Agile and tools such as Git for version control, is essential for creating robust software solutions.
Networking and Security: Basic knowledge of network protocols and cybersecurity principles is beneficial for understanding data communication and protecting systems from threats.
Problem-Solving and Critical Thinking: The ability to approach complex problems logically and creatively is vital in CS to develop innovative solutions.
Communication: Effective communication skills are necessary to explain technical concepts to non-technical stakeholders and collaborate with team members.
Teamwork: Computer scientists often work in teams; hence, the ability to collaborate effectively is crucial for project success.
Attention to Detail: Precision is key in coding and debugging; small errors can lead to significant issues.
Time Management: Managing time effectively to meet tight deadlines and juggle multiple projects is important in the fast-paced tech industry.
Adaptability: The tech field evolves rapidly; thus, being open to learning new technologies and adapting to changes is essential for long-term success
"""

# Helper function to read JSON data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {"users": [], "job_description": DEFAULT_JD}

# Helper function to save data to JSON
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Helper function to use Text-to-Speech for chatbot responses
def speak_text(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Method to generate response using OpenAI model
def generate_response(prompt, messages):
    messages.append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=messages
    )

    response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": response})

    total_tokens = completion.usage.total_tokens

    return response, total_tokens, messages

# Admin Screen
def admin_screen():
    st.title("Admin Panel")

    # Load current data
    data = load_data()

    # Admin inputs for user details
    st.subheader("Add Candidate Information")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    resume = st.text_area("Paste Resume")

    # Button to add candidate
    if st.button("Add Candidate"):
        if full_name and email and phone and resume:
            # Generate a unique ID for the candidate
            unique_id = str(uuid.uuid4())

            # Save candidate data with unique ID
            new_user = {
                "id": unique_id,
                "name": full_name,
                "email": email,
                "phone": phone,
                "resume": resume
            }
            data["users"].append(new_user)
            save_data(data)
            st.success(f"Candidate {full_name} added successfully with ID: {unique_id}")
        else:
            st.error("Please fill out all fields.")

    # Admin can update the job description
    st.subheader("Update Job Description")
    jd = st.text_area("Job Description", value=data.get("job_description", DEFAULT_JD))
    if st.button("Update JD"):
        data["job_description"] = jd
        save_data(data)
        st.success("Job Description updated successfully!")

    # Show the stored candidates
    st.subheader("Registered Candidates")
    for user in data["users"]:
        st.write(f"- {user['name']} ({user['email']}) - ID: {user['id']}")

# Candidate Screen (Quiz Section)
def candidate_screen():
    st.title("Candidate Quiz")

    # Candidate inputs their unique ID to access the quiz
    candidate_id = st.text_input("Enter your unique ID")
    data = load_data()

    # Validate candidate's ID
    candidate = next((user for user in data["users"] if user["id"] == candidate_id), None)

    if candidate:
        st.success(f"Welcome, {candidate['name']}!")
        
        # Display Job Description
        st.subheader("Job Description")
        st.write(data["job_description"])

        # Quiz Section - Same as before
        st.subheader("Quiz Section")

        # Initialize session state variables if not set
        if 'generated' not in st.session_state:
            st.session_state['generated'] = []
        if 'past' not in st.session_state:
            st.session_state['past'] = []
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [
                {"role": "system", "content": "You are an AI interviewer for the provided job description."}
            ]
        if 'total_tokens' not in st.session_state:
            st.session_state['total_tokens'] = 0

        # Text input for user response
        user_input = st.text_area("You:", key="input", height=100)
        submit_button = st.button("Send")

        # Process response if submitted
        if submit_button and user_input:
            output, total_tokens, messages = generate_response(user_input, st.session_state['messages'])

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
            st.session_state['messages'] = messages
            st.session_state['total_tokens'] += total_tokens

            # Play the response using TTS
            speak_text(output)

        # Display the conversation history
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                st.write(f"User: {st.session_state['past'][i]}")
                st.write(f"AI: {st.session_state['generated'][i]}")
    else:
        if candidate_id:
            st.error("Invalid ID. Please check your ID and try again.")

# Main App
def main():
    # Allow admin or candidate to choose their role
    role = st.sidebar.selectbox("Who are you?", ["Admin", "Candidate"])

    if role == "Admin":
        admin_screen()
    else:
        candidate_screen()

if __name__ == "__main__":
    main()
