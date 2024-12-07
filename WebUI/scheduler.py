from apscheduler.schedulers.background import BackgroundScheduler

from .caching import remove_old_images, static_cache
from .database import ImageTinderDatabase


def cache_static_images():
    """Cache static images based on the 'best_images' field in the 'collection' table.

    This function retrieves the image IDs from the 'best_images' field in the 'collection' table,
    which contains a list of image IDs (a comma-separated string). It then fetches the corresponding
    image file paths from the database and caches them using the `static_cache` function.
    """
    db = ImageTinderDatabase()
    query = """SELECT
        i.id AS image_id,
        i.file_path AS image_path
    FROM
        collection c
    JOIN
        image i ON ',' || c.best_images || ',' LIKE '%,' || i.id || ',%'
    WHERE
        c.best_images IS NOT NULL;

    """
    result = db._execute_sql(query, True)
    static_cache({key: value for key, value in result})


def define_best_images():
    """Define the top 3 rated images for each collection and updates the 'best_images' field.

    This function ranks the images for each collection based on user ratings (excluding deleted images),
    selects the top 3 images for each collection, and updates the 'best_images' field in the 'collection' table
    with the comma-separated IDs of the top 3 images.
    """
    db = ImageTinderDatabase()
    query = """WITH RankedImages AS (
                SELECT
                    c.id AS collection_id,
                    i.id AS image_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY c.id
                        ORDER BY ui.rating DESC
                    ) AS rank
                FROM
                    collection c
                JOIN
                    user_collection uc ON c.id = uc.collection_id
                JOIN
                    user_image ui ON uc.user_id = ui.user_id
                JOIN
                    image i ON ui.image_id = i.id
                WHERE
                    ui.deleted = 0
            ),
            TopImages AS (
                SELECT
                    collection_id,
                    GROUP_CONCAT(image_id) AS top_image_ids
                FROM
                    RankedImages
                WHERE
                    rank <= 3
                GROUP BY
                    collection_id
            )
            UPDATE
                collection
            SET
                best_images = COALESCE((SELECT top_image_ids FROM TopImages
                                        WHERE TopImages.collection_id = collection.id), '')
            WHERE
                id IN (SELECT collection_id FROM TopImages);
            """
    db._execute_sql(query)


def get_scheduler() -> BackgroundScheduler:
    """Create and return a background scheduler with scheduled jobs.

    This function creates an instance of `BackgroundScheduler` and adds three cron jobs to:
    1. Define the best images for collections (`define_best_images`) at 3 AM every day.
    2. Cache static images for collections (`cache_static_images`) at 4 AM every day.
    3. Remove old images from the cache (`remove_old_images`) at 5 AM every day.

    Additionally, the tasks are executed immediately when the scheduler is created.

    Returns
    -------
        BackgroundScheduler: An instance of the background scheduler with the added jobs.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(define_best_images, "cron", hour=3)
    scheduler.add_job(cache_static_images, "cron", hour=4)
    scheduler.add_job(remove_old_images, "cron", hour=5)
    define_best_images()
    cache_static_images()
    remove_old_images()
    return scheduler
