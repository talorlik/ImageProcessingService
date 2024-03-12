# Image processing service

This project is written in Python and runs a Flask server

In this project I've implemented some of the more common image actions such as: blur, contour, rotate, salt_n_pepper, concat and segment

The flask server is exposed to the world by using Ngrok and it is communicated with via a Telegram Bot.

Furthermore, the image filters were written using normal built-in Python code without any auxiliary packages for image processing.

### Basic flow
The user uploads an image or more to the bot and in the caption writes one of the actions mentioned above. The backend server processes the
request and and sends the bot the response back. In this case it'll be the resulting image after it was manipulated.

### Initiate interaction
You may type either of these three words to initiate interacting with the bot: 'start', 'help' or 'hello'

### Directory structure
```console
.
├── README.md
├── photos
└── polybot
    ├── app.py
    ├── bot.py
    ├── img_proc.py
    ├── photos
    ├── requirements.txt
    └── test
        ├── beatles.jpeg
        ├── test_concat.py
        ├── test_rotate.py
        ├── test_salt_n_pepper.py
        ├── test_segment.py
        └── test_telegram_bot.py
```

## Image class implementation

Under `polybot/img_proc.py`, the `Img` class is designed for image filtering on grayscale images.

#### Creating an instance of `Img`

Provide the path to the image file as a parameter when creating an instance of the `Img` class, for example:

```python
my_img = Img('path/to/image.jpg')
```

#### Saving the modified image

After performing operations on the image, you can save the modified image using the `save_img()` method, for example:

```python
my_img.save_img()
```

This will save the modified grayscale image to a new path with an appended `_filtered` suffix, and uses the same file extension.

### Filters

#### Concatenating images

The `concat()` method concatenates two images together horizontally or vertically (side by side).

*NOTE:* Currently 'concat' is limited to two images

It checks the dimensions of both images to ensure they are compatible for concatenation and throws a RuntimeError exception if not.
For horizontal concatenation it checks both images' height and for vertical concatenation it rotates both images by 90deg (1 time clockwise) first using the self.rotate_clockwise() method and then check the height.
In addition the user is able to choose for horizontal to concat right to left or left to right of image1 and image2 respectively and for vertical to concatenate bottom to top or top to bottom of image1 and image2 respectively (this determines how the image has to be rotated prior to being concatenated)

:param other_img: An instance of image
:param direction: Determines whether to concatenate horizontal or vertical (default "horizontal")
:param sides: based on the direction the user will be able to choose which sides of the images to concatenate (default "right-to-left")
:return new_image: A new image instance

```python
my_img = Img('path/to/image.jpg')
another_img = Img('path/to/image2.jpg')
my_img.concat(another_img)
my_img.save_img() # concatenated image was saved in 'path/to/image_filtered.jpg'
```

#### Adding "salt and pepper" noise to the image

The `salt_n_pepper()` noise method applies a type of image distortion that randomly adds isolated pixels with value of either 255 (maximum white intensity) or 0 (minimum black intensity).
The name "salt and pepper" reflects the appearance of these randomly scattered bright and dark pixels, resembling grains of salt and pepper sprinkled on an image.

:param self.data: A 2D list representing the grayscale image.
:param noise_level: A float representing the proportion of the image pixels to be affected by noise.
:return None: sets the class property data - A 2D list representing the image with salt and pepper noise applied.

```python
my_img = Img('path/to/image.jpg')
my_img.salt_n_pepper()
my_img.save_img() # noisy image was saved in 'path/to/image_filtered.jpg'
```

#### Rotating the image

The `rotate()` This method takes in a direction and degrees and rotates the image accordingly

:param direction: string of either "clockwise" or "anti-clockwise" (default "clockwise")
:param deg: integer of either 90 or 180 or 270 (default 90)
:return None: sets the class property data

```python
my_img = Img('path/to/image.jpg')
my_img.rotate()
my_img.rotate()   # rotate again for a 180 degrees rotation
my_img.save_img() # rotated image was saved in 'path/to/image_filtered.jpg'
```

#### Segmenting the image

The `segment()` method partitions the image into regions where the pixels have similar attributes, so the image is represented in a more simplified manner, and so we can then identify objects and boundaries more easily.
Segments the image by setting pixels with intensity greater than 100 to white (255), and all others to black (0).

```python
my_img = Img('path/to/image.jpg')
my_img.segment()
my_img.save_img()
```

#### Blurring the image

The `blur()` method is already implemented. You can control the blurring level `blur_level` argument (default is 16).
It blurs the image by replacing the value of each pixel by the average of the 16 pixels around him (or any other value, controlled by the `blur_level` argument. The bigger the value, the stronger the blurring level).

:param blur_level: Determines the level by which to blur the image
:return None:

```python
my_img = Img('path/to/image.jpg')
my_img.blur()   # or my_img.blur(blur_level=32) for stronger blurring effect
my_img.save_img()
```

#### Creating a contour of the image

The `contour()` method is already implemented. It applies a contour effect to the image by calculating the **differences between neighbor pixels** along each row of the image matrix.

```python
my_img = Img('path/to/image.jpg')
my_img.contour()
my_img.save_img()
```

### Filter testing locally

Under `polybot/test` you'll find unittests for each filter.

For example, to execute the test suite for the `concat()` filter, run the below command from the root dir of your repo:

```bash
python -m polybot.test.test_concat
```

An alternative way is to run tests from your favorite IDE.

## Telegram Bot

1. <a href="https://desktop.telegram.org/" target="_blank">Download</a> and install telegram desktop (you can use the app on your phone as well).
2. Once installed, create your own Telegram Bot by following <a href="https://core.telegram.org/bots/features#botfather">this section</a> to create a bot. Once you have your telegram token you can move to the next step.

**NOTE:** Keep your Telegram token safe and do not share it with anyone.

## Running the Telegram bot locally

The Telegram app is a flask-based service that is responsible for providing a chat-based interface for users to interact with an image processing functionality. It utilizes the Telegram Bot API.

The bot app is in `polybot/app.py`.
In order to run the server, you have to [provide 2 environment variables](https://www.jetbrains.com/help/objc/add-environment-variables-and-program-arguments.html#add-environment-variables):

1. `TELEGRAM_TOKEN` which is your bot token.
2. `TELEGRAM_APP_URL` which is your app public URL provided by Ngrok.

The Bot app listens for updates from the Telegram servers via a **webhook**
The Python app processes the message, executes the desired logic, and may send a response back to Telegram servers, which then delivers the response to the user.

Setting your chat app URL in Telegram Servers:

<a href="https://api.telegram.org/bot[my_bot_token]/setWebhook?url=[url_to_send_updates_to]" target="_blank">https://api.telegram.org/bot[my_bot_token]/setWebhook?url=[url_to_send_updates_to]</a>

[Ngrok](https://ngrok.com/) is used to expose the local url to the outside world and that is also the url that must be given to telegram for the webhook.

**NOTE:** Each time you run Ngrok it generates you a random url that you have to re-associate with the Telegram webhook.
In order to avoid this, there's an option in Ngrok to claim a `free` static domain which you can then use repeatably.

Sign-up for the Ngrok service (or any another tunneling service to your choice), then install the `ngrok` agent as [described here](https://ngrok.com/docs/getting-started/#step-2-install-the-ngrok-agent).

Authenticate your ngrok agent. You only have to do this once:

```console
ngrok config add-authtoken <your-authtoken>
```

Since the telegram bot service will be listening on port `8443`, start ngrok by running the following command:

```console
ngrok http --domain=<replace-with-your-ngrok-static-domain> 8443
```

Alternatively, you can set the Ngrok config with a tunnel as follows:
1. To get the path to the ngrok config yaml run the following command
```console
ngrok config check
```
2. Open the file with your favorite editor and put the following in it below what is already in it as a result of the above 'config' command
```console
tunnels:
  # This name below can be anything you wish to call it. It's just an alias
  botapp:
    proto: http
    addr: 8443
    domain: [Replace with your domain from ngrok without the 'https://']
```
3. Save and exit
4. Now you can run ngrok with the following command:
```console
ngrok start botapp
```

## Running a simple "echo" Bot - the `Bot` class

Under `polybot/bot.py` there is a class called `Bot`. This class implements a simple telegram bot, as follows.

The constructor `__init__` receives the `token` and `telegram_chat_url` arguments.
The constructor creates an instance of the `TeleBot` object, which is a pythonic interface to Telegram API. You can use this instance to conveniently communicate with the Telegram servers.
Later, the constructor sets the webhook URL to be the `telegram_chat_url`.

The `polybot/app.py` is the main app entrypoint. It's nothing but a simple flask web-server that uses a `Bot` instance to handle incoming messages, caught in the `webhook` endpoint function.

The default behavior of the `Bot` class is to "echo" the incoming messages.

## Extending the echo bot - the `QuoteBot` class

In `bot.py` there is a class called `QuoteBot` which **inherits** from `Bot`.
Upon incoming messages, this bot echoing the message while quoting the original message, unless the user is asking politely not to quote.

In `app.py`, change the instantiated instance to the `QuoteBot`:

```python
- Bot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
+ QuoteBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
```

## Building the image processing bot - the `ImageProcessingBot` class

In `bot.py` there is a class called `ImageProcessingBot` which **inherits** from `Bot`.
Upon incoming **photo messages**, this bot downloads the photos and processes them according to the **`caption`** field provided with the message.
The bot will then send the processed image to the user.

## Local testing

You can test your bot logic locally by:

```bash
python -m polybot.test.test_telegram_bot
```

Or via the UI of your favorite editor.
