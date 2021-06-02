# Карточные игры
## Участники
- Бабичев Андрей Юрьевич, 522 группа, https://github.com/AndrewBabichev
- Колмагоров Евгений Игоревич, 517 группа, https://github.com/ekolmagorov

## Постановка задачи
Реализовать приложение для игры в различные карточные игры. Предполагается реализация трёх игр:
- Блекджэк (21);
- Дурак;
- Пиковая дама;

В игре дурак предполагается возможность онлайн-игры.

## Интерфейс
Интерфейс главного меню с выбором игры:

![Main_Menu](description/Main_Menu.png "Main_Menu")

Интерфейс одной из игр (блекджэк):

![Game](description/Game.png "Game")

## How to play
## Blackjack
Цель игры - набрать больший счёт, чем противник-компьютер, но не больший чем 21 очко. Счёт складывается в зависимости от карт в руке. Каждая карта имеет свою ценность - все карты с цифрами имеют аналогичную ценность, Валет - 2 очка, Дама - 3 очка, Король - 4 очка, Туз - 11 очков. Одновременно можно иметь максим 6 карт в руке. Для добора карт необходимо нажать ПКМ на колоду. После завершения всех операций с картами необходимо нажать на кнопку Stand (Хватит) - противник-компьютер сделает свой ход и будет определён победитель.

# Queen
Цель игры - лишиться всех карт. Из руки можно сбрасывать карты одинаковый ценности, но разной масти (например, короля червей и королей бубей). Для этого необходимо кликнуть ЛКМ на две такие карты в руке. Единственная карта, которую нельзя сбросить - дама пик. По ходу игры, соперники тянут друг друга карты. Для этого в свою очередь необходимо нажать на карту в руке следующего игрока. Порядок игроков - снизу вверх. Карты можно перемещать в руке - для этого необходимо нажать ЛКМ на две такие карты. После завершения всех операций с картами необходимо нажать на кнопку Ready (Готов) - противники-компьютеры сделают свои ходы и, при наличии условий продолжения игры (у противников есть карты), ход снова перейдет игроку.

# Fool-online
Цель игры - как можно скорее избавиться от карт. В данной игре принимают участие два игрока - один атакует, другой - отбивает, и в зависимости от исхода последнего хода они могут меняться ролями. Изначально у каждого игрока в руке находится 6 карт; если отбивающийся игрок не может отбить хотя бы одну из карт, он должен взять все карты со стола - для этого необходимо нажать в правом нижнем углу на кнопку Take (Взять). Если атакующий игрок не может больше подложить карт, он должен сообщить, что произошло "бито" - для этого необходимо нажать на кнопку Ready, и право хода перейдёт к отбивающемуся игроку; когда игроку не хватает карт, он добирает их из колоды, нажимая на ЛКМ. За каждый исход игрокам начисляется разное количество очков: за победу - победителю 2 очка, проигравшему 0; за ничью - каждому по одному очку. Чтобы игрокам было интересней проводить время в игре, было создано окно для чата. Прежде чем начать игру игроки должны ввести свои имена на английском языке, после этого игрок переходит в режим ожидания, пока какой-нибудь игрок не зайдёт в игру и не присоединиться к игровой сесссии.
