import json
import shutil
import validators
from django.conf import settings
from django.shortcuts import render, redirect
from .models import *
from .forms import FormWithCaptcha
from django.core.mail import EmailMessage
from django.template.loader import get_template
import instaloader
import os
import secrets
import string
import requests
import re
import uuid


# Homepage
def home(request):
    form = FormWithCaptcha()
    return render(request, 'index.html', context={'form': form})


# Download photo video and reels
def download_photo_video_reel(request):
    # Define alert messages
    success = ''
    warning = ''
    error = ''

    # Redirect to homepage if request type is GET
    if request.method == "GET":
        return redirect('/')

    form = FormWithCaptcha(request.POST)

    if form.is_valid():

        # If user enter URL instead of username
        if not validators.url(request.POST.get('url')):
            error = 'Not a valid URL.'
            context = {
                'form': form,
                'success': success,
                'error': error,
                'warning': warning,
            }
            return render(request, 'download.html', context)

        # Create an unique ID
        uid = uuid.uuid4()

        # Create an Instaloader instance
        loader = instaloader.Instaloader()

        # Loading Session
        loader.load_session_from_file('YOUR_INSTAGRAM_USERNAME', 'public/static/session/YOUR_SESSION_FILE_NAME')

        # Get post url
        post_url = request.POST.get('url')

        # Check the url is instagram url not other url (e.g. youtube, ticktok)
        insta_url_is_vaild = re.search("instagram", post_url)

        if insta_url_is_vaild:

            extracted_shorcode_image = re.findall("^(?:.*\/p\/)([\d\w\-_]+)", post_url)  # if the post is image

            extracted_shorcode_reel = re.findall("^(?:.*\/reel\/)([\d\w\-_]+)", post_url)  # if the post is video/reel

            if extracted_shorcode_image:
                # If image
                post_shortcode = extracted_shorcode_image[0]
            else:
                # If video
                post_shortcode = extracted_shorcode_reel[0]
        else:
            error = 'Not an Instagram URL!'
            form = FormWithCaptcha()
            context = {
                'form': form,
                'error': error
            }
            return render(request, 'download.html', context)

        try:

            # Replace 'download_directory' with the directory where you want to save the images
            download_directory = 'public/static/downloads/'

            # Create the download directory if it doesn't exist
            if not os.path.exists(download_directory):
                os.makedirs(download_directory)

            # Load the post
            post = instaloader.Post.from_shortcode(loader.context, post_shortcode)

            # Check weather the post is a slider images or single image
            # if slider image then index will be greater than -1
            i = -1  # initializing the variable
            for index, sidecar_post in enumerate(post.get_sidecar_nodes()):
                i = index

            if i == -1:
                # Single image
                video_url = post.video_url  # if post.is_video is True then it will be url of video file

                image_url = post.url

                # Generating random 24 charecter file name
                random_char = (
                    ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(24)))

                if video_url is None:  # not a video but single image

                    filename = f"{download_directory}photos/{random_char}.jpg"

                    # Send a GET request to the image URL
                    response = requests.get(image_url)

                    # Save the image to a local file
                    with open(filename, 'wb') as file:
                        file.write(response.content)

                        # Store record into database so that we can flush the stored content after a certain delay
                        Files.objects.create(
                            uid=uid,
                            path=f"media/downloads/photos/{random_char}.jpg",
                            type='Image',
                            deleted=False
                        )

                else:  # video

                    filename = f"{download_directory}videos/{random_char}.mp4"

                    # Send a GET request to the video URL
                    response = requests.get(video_url)

                    # Save the image to a local file
                    with open(filename, 'wb') as file:
                        file.write(response.content)

                        # Store record into database so that we can flush the stored content after a certain delay
                        Files.objects.create(
                            uid=uid,
                            path=f"media/downloads/videos/{random_char}.mp4",
                            type='Video',
                            deleted=False
                        )

            else:  # slider image/video

                # Iterate through the slider image/video posts if available
                for index, sidecar_post in enumerate(post.get_sidecar_nodes()):

                    if sidecar_post.is_video:

                        video_url = sidecar_post.video_url

                        # Generating random 24 charecter file name
                        random_char = (
                            ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(24)))

                        filename = f"{download_directory}videos/{random_char}.mp4"

                        # Send a GET request to the video URL
                        response = requests.get(video_url)

                        # Save the video to a local file
                        with open(filename, 'wb') as file:
                            file.write(response.content)

                            # Store record into database so that we can flush the stored content after a certain delay
                            Files.objects.create(
                                uid=uid,
                                path=f"media/downloads/videos/{random_char}.mp4",
                                type='Slider Video',
                                deleted=False
                            )
                    else:

                        image_url = sidecar_post.display_url

                        # Generating random 24 character file name
                        random_char = (
                            ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(24)))

                        filename = f"{download_directory}photos/{random_char}.jpg"

                        # Send a GET request to the image URL
                        image_response = requests.get(image_url)

                        # Save the image to a local file
                        with open(filename, 'wb') as file:
                            file.write(image_response.content)

                            # Store record into database so that we can flush the stored content after a certain delay
                            Files.objects.create(
                                uid=uid,
                                path=f"media/downloads/photos/{random_char}.jpg",
                                type='Slider',
                                deleted=False
                            )

            success = "Content downloaded successfully."

        except instaloader.ProfileNotExistsException:

            error = "Profile does not exist."

        except Exception as e:
            if str(e) == 'Fetching Post metadata failed.':
                warning = 'Private or deleted content. We cannot download private or deleted content!'
            else:
                error = f"Error: {e}"

        files = Files.objects.filter(uid=uid)

        form = FormWithCaptcha()

        context = {
            'files': files,
            'form': form,
            'success': success,
            'error': error,
            'warning': warning,
        }

        return render(request, 'download.html', context)

    else:
        form = FormWithCaptcha()
        error = "Recaptcha validation failed."
        context = {'error': error, 'form': form}
        return render(request, 'index.html', context)


# Download public stories from username
def download_story(request):
    # Redirect to homepage if request type is GET
    if request.method == "GET":
        return redirect('/')
    # Define alert messages
    success = ''
    warning = ''
    error = ''

    form = FormWithCaptcha(request.POST)

    if form.is_valid():

        try:

            # If user enter URL instead of username
            profile_name = request.POST.get('user_id')
            if validators.url(profile_name):
                error = 'Not an Instagram username.'
                context = {
                    'form': form,
                    'success': success,
                    'error': error,
                    'warning': warning,
                }
                # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
                if os.path.exists(f'{profile_name}'):
                    shutil.rmtree(f'{profile_name}')
                return render(request, 'download.html', context)

            # Create an unique ID
            uid = uuid.uuid4()

            L = instaloader.Instaloader()

            # Loading Session
            L.load_session_from_file('YOUR_INSTAGRAM_USERNAME', 'public/static/session/YOUR_SESSION_FILE_NAME')

            # Get post url
            profile_name = request.POST.get('user_id')

            profile_id = L.check_profile_id(profile_name)
            pid = L.load_profile_id(profile_name)

            L.dirname_pattern = f'public/static/downloads/stories/{uid}'
            if not os.path.exists('public/static/downloads/stories/' + str(uid)):
                os.makedirs('public/static/downloads/stories/' + str(uid))

            # Download story
            L.download_stories(userids=[profile_id])

            # Store record into database so that we can flush the stored content after a certain delay
            Directories.objects.create(
                uid=uid,
                username=profile_name,
                userid=pid,
                type='story',
                deleted=False
            )

            # Read all the highlight files stored in downloads directory
            path = f'public/static/downloads/stories/' + str(uid)
            file_lists = os.listdir(path)

            filtered_story_files = []  # Filter only image and mp4 files

            for file in file_lists:
                if file.endswith(".mp4") or file.endswith(".jpg"):  # filter files by extension
                    filtered_story_files.append(file)
                    success = "Content downloaded successfully."

                    # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
                    if os.path.exists(f'{profile_name}'):
                        shutil.rmtree(f'{profile_name}')

            # Remove the video image FILENAME.jpg
            for file in filtered_story_files:
                filename = file[:-4]
                image = filename + '.jpg'
                video = filename + '.mp4'

                if video in filtered_story_files:
                    filtered_story_files.remove(image)

            if not filtered_story_files:
                error = "Could not download the story! Account is private or story may be removed."

            form = FormWithCaptcha()

            context = {
                'filtered_story_files': filtered_story_files,
                'uid': uid,
                'form': form,
                'success': success,
                'error': error,
                'warning': warning,
            }

        except Exception as e:
            error = f"Error: {e}"

            form = FormWithCaptcha()

            context = {
                'form': form,
                'success': success,
                'error': error,
                'warning': warning,
            }

        return render(request, 'download.html', context)

    else:
        form = FormWithCaptcha()
        error = "Recaptcha validation failed."
        context = {'error': error, 'form': form}
        return render(request, 'index.html', context)



# Download highlights
def download_highlight(request):
    # Redirect to homepage if request type is GET
    if request.method == "GET":
        return redirect('/')
    # Define alert messages
    success = ''
    warning = ''
    error = ''

    form = FormWithCaptcha(request.POST)

    if form.is_valid():

        try:

            # If user enter URL instead of username
            profile_name = request.POST.get('user_id')
            if validators.url(profile_name):
                error = 'Not an Instagram username.'
                context = {
                    'form': form,
                    'success': success,
                    'error': error,
                    'warning': warning,
                }
                # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
                if os.path.exists(f'{profile_name}'):
                    shutil.rmtree(f'{profile_name}')
                return render(request, 'download.html', context)

            # Create an unique ID
            uid = uuid.uuid4()

            L = instaloader.Instaloader()

            # Load Session
            L.load_session_from_file('YOUR_INSTAGRAM_USERNAME', 'public/static/session/YOUR_SESSION_FILE_NAME')

            # Get post url
            profile_name = request.POST.get('user_id')

            profile_id = L.check_profile_id(profile_name)
            pid = L.load_profile_id(profile_name)

            L.dirname_pattern = f'public/static/downloads/highlights/{uid}'
            if not os.path.exists('public/static/downloads/highlights/' + str(uid)):
                os.makedirs('public/static/downloads/highlights/' + str(uid))

            L.download_highlights(pid)

            # Store record into database so that we can flush the stored content after a certain delay
            Directories.objects.create(
                uid=uid,
                username=profile_name,
                userid=pid,
                type='Highlights',
                deleted=False
            )

            # Read all the highlight files stored in downloads directory
            path = f'public/static/downloads/highlights/' + str(uid)
            file_lists = os.listdir(path)

            filtered_highlight_files = []  # Filter only image and mp4 files

            # Sort only the Photos and Videos but not zip files
            for file in file_lists:
                if file.endswith(".mp4") or file.endswith(".jpg"):  # filter files by extension
                    filtered_highlight_files.append(file)
                    success = 'Content downloaded successfully.'
                    # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
                    if os.path.exists(f'{profile_name}'):
                        shutil.rmtree(f'{profile_name}')

            # Remove the video cover image FILENAME_cover.jpg
            for file in filtered_highlight_files:
                if file.endswith("_cover.jpg"):  # filter files by extension
                    filtered_highlight_files.remove(file)

            # Remove the video image FILENAME.jpg
            for file in filtered_highlight_files:
                filename = file[:-4]
                image = filename + '.jpg'
                video = filename + '.mp4'
                if video in filtered_highlight_files:
                    filtered_highlight_files.remove(image)

            if not filtered_highlight_files:
                error = "Could not download Highlights! Account is private or story may be removed."

            form = FormWithCaptcha()

            context = {
                'filtered_highlight_files': filtered_highlight_files,
                'uid': uid,
                'form': form,
                'success': success,
                'error': error,
                'warning': warning,
            }

        except Exception as e:

            error = f"Error: {e}"

            form = FormWithCaptcha()

            context = {
                'form': form,
                'success': success,
                'error': error,
                'warning': warning,
            }

        return render(request, 'download.html', context)

    else:

        form = FormWithCaptcha()
        error = "Recaptcha validation failed."
        context = {'error': error, 'form': form}
        return render(request, 'index.html', context)


# Download DP (Profile picture)
def download_dp(request):
    # Redirect to homepage if request type is GET
    if request.method == "GET":
        return redirect('/')

    # Define alert messages
    success = ''
    warning = ''
    error = ''

    form = FormWithCaptcha(request.POST)

    if form.is_valid():
        try:
            # If user enter URL instead of username
            profile_name = request.POST.get('user_id')
            if validators.url(profile_name):
                error = 'Not an Instagram username.'
                context = {
                    'form': form,
                    'success': success,
                    'error': error,
                    'warning': warning,
                }
                # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
                if os.path.exists(f'{profile_name}'):
                    shutil.rmtree(f'{profile_name}')
                return render(request, 'download.html', context)

            # Create an unique ID
            uid = uuid.uuid4()

            L = instaloader.Instaloader()

            # Load session
            L.load_session_from_file('YOUR_INSTAGRAM_USERNAME', 'public/static/session/YOUR_SESSION_FILE_NAME')

            # Get post url
            profile_name = request.POST.get('user_id')

            profile_id = L.check_profile_id(profile_name)
            pid = L.load_profile_id(profile_name)

            L.dirname_pattern = f'public/static/downloads/dp/{uid}'
            if not os.path.exists('public/static/downloads/dp/' + str(uid)):
                os.makedirs('public/static/downloads/dp/' + str(uid))

            # Download DP only
            L.download_profile(profile_name, profile_pic_only=True)

            # Store record into database so that we can flush the stored content after a certain delay
            Directories.objects.create(
                uid=uid,
                username=profile_name,
                userid=pid,
                type='DP',
                deleted=False
            )

            # Read all the highlight files stored in downloads directory
            path = f'public/static/downloads/dp/' + str(uid)
            file_lists = os.listdir(path)

            filtered_dp_files = []  # Filter only image and mp4 files

            for file in file_lists:
                if file.endswith(".mp4") or file.endswith(".jpg"):  # filter files by extension
                    filtered_dp_files.append(file)
                    success = 'Content downloaded successfully.'
                    # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
                    if os.path.exists(f'{profile_name}'):
                        shutil.rmtree(f'{profile_name}')

            if not filtered_dp_files:
                error = "Could not download Highlights! Account is private or story may be removed."

            form = FormWithCaptcha()
            context = {
                'filtered_dp_files': filtered_dp_files,
                'uid': uid,
                'form': form,
                'success': success,
                'error': error,
                'warning': warning,
            }

        except Exception as e:

            error = f"Error: {e}"

            form = FormWithCaptcha()

            context = {
                'form': form,
                'success': success,
                'error': error,
                'warning': warning,
            }

        return render(request, 'download.html', context)

    else:

        form = FormWithCaptcha()
        error = "Recaptcha validation failed."
        context = {'error': error, 'form': form}
        return render(request, 'index.html', context)


# Private Downloader
def instagram_private_downloader(request):
    # Define alert messages
    success = ''
    warning = ''
    error = ''
    url_photo = ''
    url_video = ''
    response_video = ''
    carousel_media_urls = []
    carousel_video = False

    if request.method == "GET":
        form = FormWithCaptcha()
        return render(request, 'private.html', context={'form': form})
    if request.method == "POST":
        form = FormWithCaptcha(request.POST)
        if form.is_valid():
            try:
                # Get json code
                json_code = request.POST.get('json_code')
                data = json.loads(json_code)

                # For video carousel post
                if 'graphql' in data:
                    if 'edge_sidecar_to_children' in data['graphql']['shortcode_media']:
                        carousel_video = True
                        carousel_size = len(data['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'])
                        carousel_data = data['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
                        for counter in range(carousel_size):
                            carousel_media_urls.append(
                                carousel_data[counter]['node']['video_url'])

                if 'items' in data:
                    if 'video_versions' in data['items'][0]:
                        url_video = data['items'][0]['video_versions'][0]['url']
                        response_video = requests.get(url_video)
                    else:
                        # For photo carousel
                        if 'carousel_media' in data['items'][0]:
                            carousel_size = len(data['items'][0]['carousel_media'])
                            carousel_data = data['items'][0]['carousel_media']
                            for counter in range(carousel_size):
                                carousel_media_urls.append(
                                    carousel_data[counter]['image_versions2']['candidates'][0]['url'])
                        else:
                            url_photo = data['items'][0]['image_versions2']['candidates'][0]['url']
                            response_photo = requests.get(url_photo)

                # Create an unique ID
                uid = uuid.uuid4()
                uid = str(uid)
                carousel_files = []
                if len(carousel_media_urls) > 0:  # if carousel
                    for url in carousel_media_urls:
                        uid = uuid.uuid4()
                        uid = str(uid)

                        if carousel_video: #video carousel
                            response_video = requests.get(url)
                            filename = (f"public/static/downloads/private/{uid}.mp4")
                            with open(filename, 'wb') as file:
                                file.write(response_video.content)
                                carousel_files.append(f"media/downloads/private/{uid}.mp4")
                            type = 'carousel video'
                        else: #image carousel
                            response_photo = requests.get(url)
                            filename = (f"public/static/downloads/private/{uid}.jpg")
                            with open(filename, 'wb') as file:
                                file.write(response_photo.content)
                                carousel_files.append(f"media/downloads/private/{uid}.jpg")
                            type = 'carousel'

                    context = {'type': type, 'carousel_files': carousel_files}
                elif url_photo:  # filter files by extension
                    filename = f"public/static/downloads/private/{uid}.jpg"
                    with open(filename, 'wb') as file:
                        file.write(response_photo.content)
                        url = '../media/downloads/private/' + str(uid) + '.jpg'
                    type = 'photo'
                    context = {'type': type, 'url': url}
                else:
                    filename = f"public/static/downloads/private/{uid}.mp4"
                    with open(filename, 'wb') as file:
                        file.write(response_video.content)
                        url = '../media/downloads/private/' + str(uid) + '.mp4'
                    type = 'video'
                    context = {'type': type, 'url': url}

            except Exception as e:
                error = f"Error: {e}"
                context = {'error': error}
        else:

            form = FormWithCaptcha()
            error = "Recaptcha validation failed."
            context = {'error': error, 'form': form}
            return render(request, 'private.html', context)

    return render(request, 'private.html', context)


# Terms page
def terms(request):
    return render(request, 'terms.html')


# Privacy page
def privacy(request):
    return render(request, 'privacy.html')


# Contact page
def contact(request):
    form = FormWithCaptcha()
    if request.method == "GET":
        return render(request, 'contact.html', context={'form': form})
    else:
        success = ''
        error = ''
        form = FormWithCaptcha()
        try:
            form = FormWithCaptcha(request.POST)
            if form.is_valid():
                name = request.POST.get('name')
                subject = request.POST.get('subject')
                message = request.POST.get('message')
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [request.POST.get('email'), ]

                context = {
                    'name': name,
                    'subject': subject,
                    'message': message,
                }

                message = get_template("email.html").render(context)
                mail = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=email_from,
                    to=['YOUR_EMAIL'],
                    reply_to=recipient_list,
                )
                mail.content_subtype = "html"
                mail.send()
                success = "Email sent successfully. We will get in touch with you soon."
                context = {'success': success, 'form': form}
            else:
                form = FormWithCaptcha()
                error = "Recaptcha validation failed."
                context = {'error': error, 'form': form}
                return render(request, 'contact.html', context)
        except Exception as e:
            error = f"Error: {e}"
            context = {'error': error, 'form': form}

        return render(request, 'contact.html', context)


# Sitemap
def sitemap(request):
    return render(request, 'sitemap.html', content_type="text/xml")
