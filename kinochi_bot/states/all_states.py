from aiogram.fsm.state import State, StatesGroup


# --------------------------- FOYDALANUVCHI ---------------------------

class UserStates(StatesGroup):
    waiting_search_query = State()
    waiting_movie_code = State()
    waiting_promo_code = State()


# --------------------------- ADMIN: KINOLAR ---------------------------

class AdminMovieAdd(StatesGroup):
    code = State()
    title = State()
    category = State()
    description = State()
    year = State()
    quality = State()
    language = State()
    is_premium = State()
    cover = State()
    video = State()


class AdminMovieEdit(StatesGroup):
    choose_code = State()
    choose_field = State()
    new_value = State()


class AdminMovieDelete(StatesGroup):
    choose_code = State()


class AdminMovieSearch(StatesGroup):
    query = State()


# --------------------------- ADMIN: SERIALLAR ---------------------------

class AdminSeriesAdd(StatesGroup):
    code = State()
    title = State()
    category = State()
    description = State()
    year = State()
    quality = State()
    language = State()
    is_premium = State()
    cover = State()
    episode_video = State()   # serial qo'shilgandan so'ng darhol qism video so'raladi


class AdminSeriesDelete(StatesGroup):
    choose_code = State()


class AdminSeriesEdit(StatesGroup):
    choose_code = State()
    choose_field = State()
    new_value = State()


class AdminEpisodeAdd(StatesGroup):
    series_code = State()
    episode_number = State()
    video = State()


class AdminEpisodeEdit(StatesGroup):
    series_code = State()
    episode_number = State()
    video = State()



# --------------------------- ADMIN: KATEGORIYALAR ---------------------------

class AdminCategory(StatesGroup):
    add_name = State()


# --------------------------- ADMIN: MAJBURIY OBUNA ---------------------------

class AdminChannel(StatesGroup):
    title = State()
    username = State()


# --------------------------- ADMIN: PREMIUM ---------------------------

class AdminPremium(StatesGroup):
    choose_plan = State()
    action_choice = State()
    duration = State()
    price = State()


# --------------------------- ADMIN: PROMO KOD ---------------------------

class AdminPromo(StatesGroup):
    code = State()
    choose_plan = State()


# --------------------------- ADMIN: OMMAVIY XABAR ---------------------------

class AdminBroadcast(StatesGroup):
    waiting_content = State()


# --------------------------- ADMIN: SOZLAMALAR ---------------------------

class AdminSettings(StatesGroup):
    edit_payment_template = State()
    edit_card_1 = State()
    edit_card_2 = State()
    edit_admin_username = State()

