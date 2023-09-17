from utils import get_database_connection
from peewee import *

db = get_database_connection()

DirectionChoices: list = [
    ('from', 'from'),
    ('to', 'to'),
]


class SystemPrompt(Model):
    """Персонажи, а точнее промты к ним."""

    id = AutoField()
    name = CharField()
    prompt = TextField()

    class Meta:
        database = db


class TelegramUser(Model):
    """Пользователь телеграмма."""

    id = AutoField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    telegram_id = BigIntegerField()
    username = CharField()
    system_prompt = ForeignKeyField(SystemPrompt, backref='system_prompt', null=True)

    class Meta:
        database = db


class Chat(Model):
    """Чаты."""

    id = AutoField()
    telegram_user = ForeignKeyField(TelegramUser, backref='telegram_user')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    direction = CharField(choices=DirectionChoices)
    message_text = TextField()

    class Meta:
        database = db


def migration():
    """Запустить миграцию."""
    db.create_tables([SystemPrompt, TelegramUser, Chat])
    SystemPrompt.get_or_create(
        name='Чарльз Фостер',
        defaults={
            'prompt': '''Ты Чарльз Фостер — экзотерический писатель, творчество которого хорошо раскупается небольшой,
                но надёжной группой читателей, интересующихся спиритуализмом, всякими нематериальными явлениями,
                Атлантидой, летающими тарелками и Новой Эрой в технологии. Пишет он только о том, что достаточно 
                xорошо изучил, в чём участвовал лично. Темой его очередной книг
                является четвёртое измерение — время,
                 и с помощью устройства, основанного на принципе гиперкуба, 
                он намерен пройти по этой мистической тропе.'''
        }
    )
    SystemPrompt.get_or_create(
       name='Марвин Флинн',
       defaults={
        'prompt': '''
            Ты  землянин  Марвин  Флинн. Ты решил посетить Марс в туристических целях
             и выбирает для этого недорогой,но рискованный метод — обмен разумов с таким
             же, как он, обычным жителем Марса.При этом его разум переселяется в тело марсианина
             по имени Зе Краггаш, а марсианин оказывается в теле землянина.
        '''
    }
)

db.connect()
migration()
