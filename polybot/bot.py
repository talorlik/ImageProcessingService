import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img

class ExceptionHandler(telebot.ExceptionHandler):
    """
    An implementation of the telegram bot exception handler class
    """
    def __init__(self, bot):
        self.bot = bot
        self._chat_id = None

    @property
    def chat_id(self):
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value):
        self._chat_id = value

    def handle(self, exception):
        if self._chat_id is not None:
            return self.bot.send_text(self.chat_id, f"An error has ocurred:\n{exception}")
        return False

class Bot:

    def __init__(self, token, telegram_chat_url):
        self.telegram_chat_url = telegram_chat_url
        # Create a new instance of the TeleBot class.
        # All communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # Remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # Set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        # Initiate the exception handler and pass it the bot object to handle messages
        self.telegram_bot_client.exception_handler = ExceptionHandler(self)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def handle_exception(self, exception, chat_id):
        """
        This is a wrapper function which makes use of the exception handling mechanism
        By using it this way it maintains context hence when the ExceptionHandler sends a message it's as if it was sent
        by the bot itself.
        """
        exception_handler = self.telegram_bot_client.exception_handler
        exception_handler.chat_id = chat_id
        exception_handler.handle(exception)

    # TODO: This is an attempt to be creative with the code but it hasn't worked well. Some more thought is needed here
    # def create_child(self, bot_type, chat_id):
    #     """
    #     This method makes use of the factory pattern to create the right bot type for the right use
    #     """
    #     # Passing parent attributes to the child constructor
    #     try:
    #         if bot_type == 'quote':
    #             return QuoteBot(self.telegram_bot_client.token, self.telegram_chat_url)
    #         elif bot_type == 'image':
    #             return ImageProcessingBot(self.telegram_bot_client.token, self.telegram_chat_url)
    #         else:
    #             raise ValueError("Unimplemented bot type. Unable to handle this message. Please try again")
    #     except ValueError as e:
    #         self.handle_exception(e, chat_id)

    def send_welcome(self, chat_id):
        text = '''
Welcome to the Image Processing Bot!

Upload an image and type in the caption the action you'd like to do.

*NOTE:* You need to type in the words or numbers. For *Concat* you need to upload more than one image

These are the available actions:
1. *Blue* - blurs the image.
    a. You may specify noise level by inputting a floating point number

    *example usage: blur 10*
2. *Contour* - applies a contour effect to the image

    *example usage: contour*
3. *Rotate* - rotates the image
    a. You may also input either *clockwise* or *anti-clockwise* (default *clockwise*)
    b. You may also input the degrees to rotate (default *90*)
        i. *90*
        ii. *180*
        iii. *270*
    c. You may enter either of the above or both

    *example usage: anti-clockwise 180*
4. *Salt and pepper* - randomly sprinkle white and black pixels on the image
    a. You may specify noise level by inputting a floating point number representing the proportion of the image pixels to be affected by noise.

    *example usage: salt and pepper 0.1*
5. *Concat* - concatenates two or more images
    a. You may also send the direction of either *horizontal* or *vertical* (default *horizontal*)
    b. You may also specify the sides to be concatenated based on the direction (default *right-to-left*)
        i. horizontal: *right-to-left*, *left-to-right*
        ii. vertical: *top-to-bottom*, *bottom-to-top*

    *example usage: concat vertical top-to-bottom*
6. *Segment* - represented in a more simplified manner, and so we can then identify objects and boundaries more easily.

    *example usage: segment*
'''
        self.telegram_bot_client.send_message(chat_id, text, parse_mode="Markdown")

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def is_current_msg_photo(self, msg):
        return "photo" in msg

    def is_a_reply(self, msg):
        return "reply_to_message" in msg

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']

        text = msg["text"].lower()
        if any(substring in text for substring in ["start", "help", "hello"]):
            self.send_welcome(chat_id)
        else:
            self.send_text(chat_id, f'Your original message: {msg["text"]}')

class QuoteBot(Bot):
    """
    This bot is an extension of the original bot and is dedicated for sending quoted text
    """
    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def handle_message(self, msg):
        """Quote Bot message handler"""
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])

class ImageProcessingBot(Bot):
    """
    This bot is an extension of the original bot and is dedicated for image processing operations
    """

    def __init__(self, token, telegram_chat_url):
        super().__init__(token, telegram_chat_url)
        self.media_groups = {}
        self.direction = None
        self.sides = None

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return file_info.file_path:
        """
        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        try:
            with open(file_info.file_path, 'wb') as photo:
                photo.write(data)
        except OSError as e:
            self.handle_exception(f"{e}\nPlease try again.", msg["chat"]["id"])
            return None

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        try:
            if not os.path.exists(img_path):
                raise RuntimeError("Image path doesn't exist. Please try again")
        except RuntimeError as e:
            self.handle_exception(e, chat_id)
            return

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        if not self.is_current_msg_photo(msg):
            super().handle_message(msg)
            return

        """Image Bot message handler"""
        logger.info(f"Incomming image message {msg}")
        chat_id = msg['chat']['id']

        # Check whether a caption was sent and if so assign to variable
        caption = (lambda x: x.strip().lower() if x is not None else None)(msg.get("caption"))
        # Check wether the incoming image is part of a media group i.e. more than one image was sent
        media_group_id = (lambda x: x if x is not None else None)(msg.get("media_group_id"))
        try:
            if not caption and not media_group_id:
                raise RuntimeError("Please specify an action you'd like to execute on the image and try again.\nIf you're unsure, please refer to 'help' for assistance and try again.")

            if caption:
                if not any(substring in caption for substring in ["blur", "contour", "rotate", "salt and pepper", "concat", "segment"]):
                    raise ValueError("Invalid image action specified. Please refer to the 'help' for assistance and try again.")

                if "concat" in caption and not media_group_id:
                    raise RuntimeError("You need to upload more than one image in order to concat. Please try again.")
        except ValueError as e:
            self.handle_exception(e, chat_id)
            return
        except RuntimeError as e:
            self.handle_exception(e, chat_id)
            return

        image_path = self.download_user_photo(msg)
        if image_path:
            try:
                img = Img(image_path)
            except Exception as e:
                self.handle_exception(f"{e}\nPlease try again.", chat_id)
                return

            if (caption and "concat" in caption) or media_group_id:
                if caption:
                    instruction = caption.replace("concat", "").strip()

                    if instruction:
                        for substring in ["horizontal", "vertical"]:
                            if substring in instruction:
                                self.direction = substring
                                break
                        if self.direction:
                            instruction = instruction.replace(self.direction, "").strip()

                        if instruction:
                            self.sides = instruction

                # Initialize the group in the dictionary if it doesn't exist
                if media_group_id not in self.media_groups:
                    self.media_groups[media_group_id] = []

                self.media_groups[media_group_id].append(img)

                if len(self.media_groups[media_group_id]) > 1:
                    try:
                        if self.direction and self.sides:
                            self.media_groups[media_group_id][0].concat(self.media_groups[media_group_id][1], self.direction, self.sides)
                        elif self.direction:
                            self.media_groups[media_group_id][0].concat(self.media_groups[media_group_id][1], direction=self.direction)
                        elif self.sides:
                            self.media_groups[media_group_id][0].concat(self.media_groups[media_group_id][1], sides=self.sides)
                        else:
                            self.media_groups[media_group_id][0].concat(self.media_groups[media_group_id][1])

                        image_path = self.media_groups[media_group_id][0].save_img()
                        # Send the response with the modified image back to the bot
                        self.send_photo(chat_id, image_path)
                    except ValueError as e:
                        self.handle_exception(f"{e}\nPlease try again.", chat_id)
                        return
                    except RuntimeError as e:
                        self.handle_exception(f"{e}\nPlease try again.", chat_id)
                        return
                    except Exception as e:
                        self.handle_exception(f"{e}\nPlease try again.", chat_id)
                        return
                    finally:
                        # Clean the handled group from the media groups dictionary and reset the direction and sides
                        del self.media_groups[media_group_id]
                        self.direction = None
                        self.sides = None
            else:
                try:
                    if "blur" in caption:
                        blur_level = caption.replace("blur", "").strip()
                        if blur_level:
                            img.blur(blur_level)
                        else:
                            img.blur()
                    elif "contour" in caption:
                        img.contour()
                    elif "rotate" in caption:
                        direction = None
                        degree = None
                        instruction = caption.replace("rotate", "").strip()
                        if instruction:
                            for substring in ["anti-clockwise", "clockwise"]:
                                if substring in instruction:
                                    direction = substring
                                    break
                            if direction:
                                instruction = instruction.replace(direction, "").strip()

                            if instruction:
                                degree = instruction

                        if direction and degree:
                            img.rotate(direction, degree)
                        elif direction:
                            img.rotate(direction=direction)
                        elif degree:
                            img.rotate(deg=degree)
                        else:
                            img.rotate()
                    elif "salt and pepper" in caption:
                        noise_level = caption.replace("salt and pepper", "").strip()
                        if noise_level:
                            img.salt_n_pepper(noise_level)
                        else:
                            img.salt_n_pepper()
                    elif "segment" in caption:
                        img.segment()

                    image_path = img.save_img()
                    # Send the response with the modified image back to the bot
                    self.send_photo(chat_id, image_path)
                except ValueError as e:
                    self.handle_exception(f"{e}\nPlease try again.", chat_id)
                    return
                except Exception as e:
                    self.handle_exception(f"{e}\nPlease try again.", chat_id)
                    return
