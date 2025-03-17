// Шаблон для header
const headerTemplate = `
    <header class="header">
        <nav class="header--menu"> 
            <div class="header--menu--icon"></div>
            <ul class="header--menu--list">
                <li class="header--menu--list--li"><a href="/">Главная</a></li>
                <li class="header--menu--list--li"><a href="/about">Электронные книжные выставки</a></li>
                <li class="header--menu--list--li"><a href="/contact">Констуктор</a></li>
                <li class="header--menu--list--li register"><a href="/user-login/">Вход</a></li>
            </ul>
        </nav>
    </header>
`;
const footerTemplate = `
    <footer class="footer">
        <div class="footer--head">
            <span>ЭКВ</span>
        </div>
        <div class="footer--mid">
            <div class="footer--mid--navigation">
                <span>Навигация</span>
                <span>Главная</span>
                <span>Электронная книжная выставка</span>
                <span>Конструктор электронной книжной выставки</span>
                <span>Войти</span>
            </div>
            <div class="footer--mid--navigation">
                <span>Контакты</span>
                <span>+7 964 422 07 09</span>
                <div class="footer--mid--navigation-icon">
                </div>
            </div>
            <div class="footer--mid--navigation">
                <span>Адрес</span>
            </div>
        </div>
        <div class="footer--footer">
            <span>ЭКВ</span>
        </div>
    </footer>
`;

// Вставляем шаблоны в соответствующие места
document.getElementById('header-placeholder').innerHTML = headerTemplate;
document.getElementById('footer-placeholder').innerHTML = footerTemplate;