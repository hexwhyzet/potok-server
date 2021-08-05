from potok_app.config import Config
from potok_app.functions import id_gen
from potok_app.models import PictureData
from potok_app.object_storage_api import upload_picture_bytes
from potok_app.picture_editor import resize_and_compress

config = Config()

SIZE_CHART = {
    PictureData.PictureDataSizeType.TINY: 80,
    PictureData.PictureDataSizeType.SMALL: 160,
    PictureData.PictureDataSizeType.MEDIUM: 320,
    PictureData.PictureDataSizeType.BIG: 640,
    PictureData.PictureDataSizeType.HUGE: 1280,
}


def create_picture_data_of_all_sizes(content_object, picture_bytes, extension):
    results = []
    for size_type, max_side_size in SIZE_CHART.items():
        resized_picture_bytes, resized_width, resized_height, picture_was_resized = resize_and_compress(picture_bytes,
                                                                                                        extension,
                                                                                                        max_side_size)
        path = upload_picture_bytes(resized_picture_bytes,
                                    f'{config["image_server_directory"]}/{id_gen(50)}.{extension}')
        picture_data = create_picture_data(content_object=content_object, path=path, size_type=size_type,
                                           width=resized_width, height=resized_height)
        results.append(picture_data)
        if not picture_was_resized:
            break
    return results


def create_picture_data(content_object, path: str, size_type: PictureData.PictureDataSizeType,
                        height: int, width: int):
    return PictureData.objects.create(content_object=content_object, path=path, size_type=size_type,
                                      height=height, width=width)


def get_picture_data_by_content_object(content_object):
    return PictureData.objects.filter(content_type__model=content_object.__class__.__name__.lower(),
                                      object_id=content_object.id)


def delete_picture_data_by_content_object(content_object):
    return get_picture_data_by_content_object(content_object).delete()
