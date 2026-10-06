import streamlit as st
import requests
import uuid
import re


# ---------------------------------------------------------
# RASA ADDRESS
# ---------------------------------------------------------

RASA_URL = "http://127.0.0.1:5005/webhooks/rest/webhook"


# ---------------------------------------------------------
# SESSION VALUES
# ---------------------------------------------------------

if "sender_id" not in st.session_state:
    st.session_state["sender_id"] = str(uuid.uuid4())


if "messages" not in st.session_state:
    st.session_state["messages"] = []


if "quick_replies" not in st.session_state:
    st.session_state["quick_replies"] = []


if "handover_active" not in st.session_state:
    st.session_state["handover_active"] = False


# ---------------------------------------------------------
# FUNCTION FOR COLOUR-CODED CARBON RESULT
# ---------------------------------------------------------

def show_carbon_card(text):

    # Find a carbon value such as:
    # Carbon: 17.5 kg CO2e

    match = re.search(
        r"Carbon:\s*([\d.]+)\s*kg",
        text,
        re.IGNORECASE
    )


    if not match:

        st.write(text)
        return


    carbon = float(
        match.group(1)
    )


    # Simple environmental impact levels

    if carbon < 25:

        st.success(text)


    elif carbon < 75:

        st.warning(text)


    else:

        st.error(text)


# ---------------------------------------------------------
# DISPLAY A BOT MESSAGE
# ---------------------------------------------------------

def show_bot_message(message):

    text = message["content"]


    # Transport comparison contains several sections
    if message.get("carbon_cards"):

        sections = text.split("\n\n")


        for section in sections:

            if "Carbon:" in section:

                show_carbon_card(
                    section
                )

            else:

                st.write(
                    section
                )


    else:

        st.write(
            text
        )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title(
    "Navigation"
)

st.sidebar.markdown(
    "Use this panel to use the Eco Travel Bot"
)


page = st.sidebar.selectbox(
    "Go to",
    [
        "Home",
        "Chat",
        "About"
    ]
)


# ---------------------------------------------------------
# HUMAN HANDOVER INDICATOR
# ---------------------------------------------------------

if st.session_state["handover_active"]:

    st.sidebar.warning(
        "Human advisor handover active"
    )


# ---------------------------------------------------------
# CLEAR CHAT
# ---------------------------------------------------------

if page == "Chat":

    clear_chat = st.sidebar.button(
        "Clear Chat History"
    )


    if clear_chat:

        st.session_state["messages"] = []

        st.session_state[
            "quick_replies"
        ] = []

        st.session_state[
            "handover_active"
        ] = False

        # New Rasa conversation
        st.session_state[
            "sender_id"
        ] = str(
            uuid.uuid4()
        )

        st.rerun()


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title(
    "Eco Travel Assistant"
)

st.divider()


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

if page == "Home":

    st.header(
        "Welcome"
    )

    st.write(
        "This chatbot gives simple travel information "
        "with a sustainability focus."
    )

    st.write(
        "Select Chat from the sidebar to start."
    )


# ---------------------------------------------------------
# CHAT
# ---------------------------------------------------------

elif page == "Chat":

    st.header(
        "Chat"
    )


    # Show handover notice
    if st.session_state[
        "handover_active"
    ]:

        st.warning(
            "This conversation has been prepared "
            "for a human travel advisor."
        )


    # -----------------------------------------------------
    # DISPLAY CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state[
        "messages"
    ]:

        with st.chat_message(
            message["role"]
        ):

            if message["role"] == "assistant":

                show_bot_message(
                    message
                )

            else:

                st.write(
                    message["content"]
                )


    # -----------------------------------------------------
    # VALUES USED FOR SENDING MESSAGES
    # -----------------------------------------------------

    message_to_send = None
    display_message = None


    # -----------------------------------------------------
    # DYNAMIC RASA QUICK REPLIES
    # -----------------------------------------------------

    if st.session_state[
        "quick_replies"
    ]:

        st.write(
            "Choose an option:"
        )


        buttons = st.session_state[
            "quick_replies"
        ]


        columns = st.columns(
            min(
                len(buttons),
                3
            )
        )


        for index, button in enumerate(
            buttons
        ):

            column = columns[
                index % len(columns)
            ]


            with column:

                if st.button(
                    button["title"],
                    key="quick_" + str(index)
                ):

                    message_to_send = button[
                        "payload"
                    ]

                    display_message = button[
                        "title"
                    ]

                    st.session_state[
                        "quick_replies"
                    ] = []


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    user_input = st.chat_input(
        "Type your message here"
    )


    if user_input:

        message_to_send = user_input
        display_message = user_input


    # -----------------------------------------------------
    # GENERAL QUICK QUESTIONS
    # -----------------------------------------------------

    if not st.session_state[
        "quick_replies"
    ]:

        st.write(
            "Quick questions:"
        )


        col1, col2, col3 = st.columns(
            3
        )


        with col1:

            if st.button(
                "Hotels in Lisbon"
            ):

                message_to_send = (
                    "find hotels in Lisbon"
                )

                display_message = (
                    "Hotels in Lisbon"
                )


        with col2:

            if st.button(
                "Weather in Berlin"
            ):

                message_to_send = (
                    "weather in Berlin"
                )

                display_message = (
                    "Weather in Berlin"
                )


        with col3:

            if st.button(
                "Plan a trip"
            ):

                message_to_send = (
                    "/start_trip_plan"
                )

                display_message = (
                    "Plan a trip"
                )


    # -----------------------------------------------------
    # SEND MESSAGE TO RASA
    # -----------------------------------------------------

    if message_to_send:

        # Save user message
        st.session_state[
            "messages"
        ].append(
            {
                "role": "user",
                "content": display_message
            }
        )


        try:

            response = requests.post(
                RASA_URL,

                json={
                    "sender": st.session_state[
                        "sender_id"
                    ],

                    "message": message_to_send
                },

                timeout=120
            )


            response.raise_for_status()

            rasa_replies = response.json()


            reply_parts = []
            new_buttons = []


            for item in rasa_replies:

                if "text" in item:

                    reply_parts.append(
                        item["text"]
                    )


                if "buttons" in item:

                    for button in item[
                        "buttons"
                    ]:

                        new_buttons.append(
                            button
                        )


            if reply_parts:

                reply = "\n\n".join(
                    reply_parts
                )

            else:

                reply = (
                    "I did not understand that."
                )


            # ---------------------------------------------
            # Detect human handover
            # ---------------------------------------------

            if (
                "HUMAN ADVISOR HANDOVER"
                in reply
            ):

                st.session_state[
                    "handover_active"
                ] = True


            # ---------------------------------------------
            # Detect transport recommendation
            # ---------------------------------------------

            has_carbon_cards = (
                "Carbon:" in reply
                and
                "kg CO2e" in reply
            )


            # Save quick replies
            st.session_state[
                "quick_replies"
            ] = new_buttons


        except requests.exceptions.RequestException as error:

            reply = (
                "Could not reach Rasa.\n\n"
                + str(error)
            )

            has_carbon_cards = False


        # Save assistant message
        st.session_state[
            "messages"
        ].append(
            {
                "role": "assistant",
                "content": reply,
                "carbon_cards": has_carbon_cards
            }
        )


        st.rerun()


# ---------------------------------------------------------
# ABOUT
# ---------------------------------------------------------

elif page == "About":

    st.header(
        "About"
    )

    st.write(
        "Built with Rasa 3.6.21, Python, "
        "Streamlit and travel APIs."
    )

    st.write(
        "This is a student-level prototype "
        "for an eco-travel chatbot."
    )

    st.write(
        "Carbon information is presented using "
        "green, amber and red indicators to help "
        "users compare environmental impact."
    )