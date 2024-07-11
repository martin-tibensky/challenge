@dataclass
class Message:
    message: str
    responseId: str
    role: str
    isGoodResponse: Optional[bool] = None


@dataclass
class Conversation:
    user_messages: Dict[str, Message] = field(default_factory=dict)
    chatbot_responses: Dict[str, Message] = field(default_factory=dict)

    def add_user_message(self, message: Message):
        if message.role != "User":
            raise ValueError("Message role must be 'User'")
        self.user_messages[message.responseId] = message

    def add_chatbot_response(self, response: Message):
        if response.role != "Chatbot":
            raise ValueError("Message role must be 'Chatbot'")
        self.chatbot_responses[response.responseId] = response

    def get_conversation_pairs(self) -> List[Tuple[Message, Message]]:
        conversation_pairs = []
        for responseId, user_message in self.user_messages.items():
            if responseId in self.chatbot_responses:
                chatbot_response = self.chatbot_responses[responseId]
                conversation_pairs.append((user_message, chatbot_response))
        return conversation_pairs

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> "Conversation":
        conversation = cls()
        queries = data["props"]["pageProps"]["appProps"]["reactQueryState"]["queries"]
        # Locate the correct query that contains the "pages" key
        for query in queries:
            if (
                "state" in query
                and "data" in query["state"]
                and "pages" in query["state"]["data"]
            ):
                pages = query["state"]["data"]["pages"]
                break
        else:
            raise ValueError("Pages data not found in the provided JSON.")

        for page in pages:
            for message_data in page["messages"]:
                message = Message(
                    message=message_data["message"],
                    responseId=message_data["responseId"],
                    role=message_data["role"],
                    isGoodResponse=message_data.get("isGoodResponse"),
                )
                if message.role == "User":
                    conversation.add_user_message(message)
                elif message.role == "Chatbot":
                    conversation.add_chatbot_response(message)
        return conversation

    def dump_conversation_pairs(self):
        for user_msg, chatbot_resp in self.get_conversation_pairs():
            print(f"User: {user_msg.message}")
            print(f"Chatbot: {chatbot_resp.message}")


def extract_conversation(page):
    messages = []

    # Select all message elements
    message_elements = page.query_selector_all(".message")

    for element in message_elements:
        user_element = element.query_selector(".bg-quartz-700, .bg-coral-900")
        text_elements = element.query_selector_all(
            '[data-element="Text"] [data-component="P"]'
        )
        if user_element and text_elements:
            user_role = (
                "user"
                if "bg-quartz-700" in user_element.get_attribute("class")
                else "chatbot"
            )
            message_text = "\n".join(
                [text_element.inner_text().strip() for text_element in text_elements]
            )
            # message_text = text_element.inner_text().strip()
            messages.append((user_role, message_text))

    return messages


def test_next_data(chat_page: Page) -> None:
    chat_page.get_by_placeholder("Message...").click()
    chat_page.get_by_placeholder("Message...").fill("Blabla\nvacica\nrosomak")
    chat_page.get_by_placeholder("Message...").press("Enter")
    chat_page.wait_for_selector('button[aria-label="approve feedback"]')
    script_content = chat_page.inner_html("#__NEXT_DATA__")
    data = json.loads(script_content)
    print(data)
    conversation = Conversation.from_data(data)
    conversation.dump_conversation_pairs()
    chat_page.pause()
