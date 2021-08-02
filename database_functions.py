import psycopg2
from datetime import datetime

host = None
database = None
user = None
password = None
port = None

# names for the tables
birthdays_table_name = 'birthdays'
birthday_channels_table_name = 'birthday_channels'

# names for the columns of the tables
user_id_column = 'user_id'
user_name_column = 'user_name'
guild_id_column = 'guild_id'
guild_name_column = 'guild_name'
month_column = 'month'
day_column = 'day'
bday_channel_id_column = 'birthday_channel_id'
bday_channel_name_column = 'birthday_channel_name'


def create_connection():
    """Creates and returns a connection to the database."""
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            port=port,
            user=user,
            password=password
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def close_connection(conn):
    """Closes the connection to the database."""
    if conn is not None:
        conn.close()


def create_tables():
    """
    Creates the tables necessary for the bot's features.

    At the moment, these are 2 tables to hold birthdays and birthday channels.
    """

    conn = create_connection()
    if conn is None:
        return

    # query to create the table that holds birthdays
    query = f"""
            CREATE TABLE IF NOT EXISTS {birthdays_table_name} ( 
                {user_id_column} BIGINT,
                {user_name_column} VARCHAR(50),
                {guild_id_column} BIGINT,
                {guild_name_column} VARCHAR(50),
                {month_column} SMALLINT,
                {day_column} SMALLINT,
                PRIMARY KEY({user_id_column}, {guild_id_column})
            );
            """
    # query to create the table that holds birthday channels
    query += f"""
            CREATE TABLE IF NOT EXISTS {birthday_channels_table_name} (
                {guild_id_column} BIGINT,
                {guild_name_column} VARCHAR(50),
                {bday_channel_id_column} BIGINT,
                {bday_channel_name_column} VARCHAR(50),
                PRIMARY KEY({guild_id_column})
            );
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
    close_connection(conn)


def insert_birthday(user_info_class):
    """
    Inserts a user and their birthday into the birthdays table.

    Parameters:
    user_info_class (UserInfo): Contains info such as user id, guild id, and birthday.

    Returns:
    bool: True if successfully inserted, false otherwise.
    """

    conn = create_connection()
    if conn is None:
        return False

    # query to insert a user's info into the table. if they are already in the table, update their name and birthday
    query = f"""
            INSERT INTO {birthdays_table_name}
            VALUES ({user_info_class.user_id}, '{user_info_class.user_name}', {user_info_class.guild_id},
                    '{user_info_class.guild_name}', {user_info_class.month}, {user_info_class.day})
            ON CONFLICT ({user_id_column}, {guild_id_column})
            DO
                UPDATE SET 
                    {user_name_column} = '{user_info_class.user_name}',
                    {guild_name_column} = '{user_info_class.guild_name}',
                    {month_column} = {user_info_class.month},
                    {day_column} = {user_info_class.day};
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows_inserted = cur.rowcount
    close_connection(conn)

    if rows_inserted > 0:
        return True
    return False


def delete_birthday(user_id, guild_id):
    """
    Deletes a user and their birthday from the birthdays table if they can be found.

    Parameters:
    user_id (int): the user's discord id.
    guild_id (int): the id of the user's guild.

    Returns:
    bool: True if successfully deleted, false otherwise.
    """

    conn = create_connection()
    if conn is None:
        return False

    query = f"""
            DELETE FROM {birthdays_table_name}
            WHERE {user_id_column} = {user_id} AND {guild_id_column} = {guild_id};
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows_deleted = cur.rowcount
    close_connection(conn)

    if rows_deleted > 0:
        return True
    return False


def get_birthday(user_id, guild_id):
    """
    Fetches a user's info from the birthday table.

    Parameters:
    user_id (int): the user's discord id.
    guild_id (int): the id of the user's guild.

    Returns:
    tuple: Contains (month, day) of user's birthday. If not found, returns (-1, -1).
    """

    conn = create_connection()
    if conn is None:
        return (-1, -1)

    query = f"""
            SELECT {month_column}, {day_column}
            FROM {birthdays_table_name}
            WHERE {user_id_column} = {user_id} AND {guild_id_column} = {guild_id};
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            birthday = cur.fetchone()
    close_connection(conn)

    if birthday is None:  # birthday not found
        return (-1, -1)
    return birthday


def insert_birthday_channel(chan_info_class):
    """
    Inserts a birthday channel into the birthday channels table.

    Parameters:
    chan_info_class (BirthdayChannelInfo): Contains info such as guild id and birthday channel id.

    Returns:
    bool: True if successfully inserted, false otherwise.
    """

    conn = create_connection()
    if conn is None:
        return False

    query = f"""
            INSERT INTO {birthday_channels_table_name}
            VALUES ({chan_info_class.guild_id}, '{chan_info_class.guild_name}', {chan_info_class.birthday_channel_id},
                    '{chan_info_class.birthday_channel_name}')
            ON CONFLICT ({guild_id_column})
            DO
                UPDATE SET
                    {guild_name_column} = '{chan_info_class.guild_name}',
                    {bday_channel_id_column} = {chan_info_class.birthday_channel_id},
                    {bday_channel_name_column} = '{chan_info_class.birthday_channel_name}';
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows_inserted = cur.rowcount
    close_connection(conn)

    if rows_inserted > 0:
        return True
    return False


def delete_birthday_channel(guild_id):
    """
    Deletes the birthday channel of a guild from the birthday channels table.

    Parameters:
    guild_id (int): The id of the guild of the birthday channel to be deleted.

    Returns:
    bool: True if successfully deleted, false otherwise.
    """

    conn = create_connection()
    if conn is None:
        return False

    query = f"""
            DELETE FROM {birthday_channels_table_name}
            WHERE {guild_id_column} = {guild_id};
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows_deleted = cur.rowcount
    close_connection(conn)

    if rows_deleted > 0:
        return True
    return False


def get_birthday_channel_id(guild_id):
    """
    Fetches the id of the birthday channel of a guild from the birthday channels table.

    Parameters:
    guild_id (int): The id of the guild of the birthday channel to be searched for.

    Returns:
    int: The birthday channel's id. Returns -1 if not found.
    """

    conn = create_connection()
    if conn is None:
        return -1

    query = f"""
            SELECT {bday_channel_id_column}
            FROM {birthday_channels_table_name}
            WHERE {guild_id_column} = {guild_id};
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            channel_id = cur.fetchone()
    close_connection(conn)

    if channel_id is None:
        return -1
    return channel_id[0]


def get_birthdays_today():
    """
    Fetches the user id and birthday channel id of each user that has a birthday today.

    The birthday channel id is used to send a birthday message to the user.

    Returns:
    list of tuples: Each tuple contains (user_id, birthday_channel_id). List will be empty if no birthdays today.
    """

    conn = create_connection()
    if conn is None:
        return []

    today = datetime.today()
    query = f"""
            SELECT {user_id_column}, {bday_channel_id_column}
            FROM {birthdays_table_name}
            INNER JOIN {birthday_channels_table_name}
            ON {birthdays_table_name}.{guild_id_column} = {birthday_channels_table_name}.{guild_id_column}
            WHERE {month_column} = {today.month} AND {day_column} = {today.day};
            """

    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            birthdays_list = cur.fetchall()
    close_connection(conn)

    return birthdays_list
