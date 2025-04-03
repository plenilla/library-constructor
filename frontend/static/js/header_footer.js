// Шаблон для header
const headerTemplate = `
    <header class="header">
        <nav class="header--menu"> 
            <div class="header--menu--icon"></div>
            <ul class="header--menu--list">
                <li class="header--menu--list--li"><a href="/">Главная</a></li>
                <li class="header--menu--list--li register"><a href="/user-login/">Вход</a></li>
            </ul>
        </nav>
    </header>
`;
const footerTemplate = `
    <footer class="footer">
        <div class="footer__head">
                <span>Контакты</span>
                <span>+7 964 422 07 09</span>
        </div>
        <div class="footer__footer">
                <span>Адрес</span>
                <span>Ул. д5</span>
        </div>
    </footer>
`;

// Вставляем шаблоны в соответствующие места
document.getElementById('header-placeholder').innerHTML = headerTemplate;
document.getElementById('footer-placeholder').innerHTML = footerTemplate;