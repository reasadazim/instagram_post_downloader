import os
import shutil

from ..models import Files, Directories


def delete_downloads():
    queryset_files = Files.objects.filter(deleted=0)
    queryset_directories = Directories.objects.filter(deleted=0)

    for file in queryset_files:

        file_path = file.path
        file_path = file_path[5:]
        file_path = f'public/static{file_path}'
        # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
        if os.path.exists(f'{file_path}'):
            os.remove(f'{file_path}')
            update = Files.objects.get(uid=file.uid)
            update.delete()

    for file in queryset_directories:

        directory_path = file.uid

        # Delete DP directory
        directory_path = f'public/static/downloads/dp/{directory_path}'
        # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
        if os.path.exists(f'{directory_path}'):
            shutil.rmtree(f'{directory_path}')
            update = Directories.objects.get(uid=file.uid)
            update.delete()

        # Delete stories directory
        directory_path = f'public/static/downloads/stories/{directory_path}'
        # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
        if os.path.exists(f'{directory_path}'):
            shutil.rmtree(f'{directory_path}')
            update = Directories.objects.get(uid=file.uid)
            update.delete()

        # Delete highlights directory
        directory_path = f'public/static/downloads/highlights/{directory_path}'
        # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
        if os.path.exists(f'{directory_path}'):
            shutil.rmtree(f'{directory_path}')
            update = Directories.objects.get(uid=file.uid)
            update.delete()

        # remove all private download files
        path = f'public/static/downloads/private/'
        file_lists = os.listdir(path)
        for file in file_lists:
            file_path = f'public/static/downloads/private/{file}'
            # Instaloader creates a directory same as profile_name. So delete that after successful DP scrap
            if os.path.exists(f'{file_path}'):
                os.remove(f'{file_path}')