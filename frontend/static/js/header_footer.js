document.addEventListener('DOMContentLoaded', function() {
    // Шаблон для header
    const headerTemplate = `
        <header class="header">
            <nav class="header--menu"> 
                <div class="header--menu--icon"></div>
                <ul id="auth-buttons" class="header--menu--list" >
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

    updateHeader();
});
async function updateHeader(){
    try {
        const response = await fetch('/users/check_auth');
        const data = await response.json();
        const authButtons = document.getElementById('auth-buttons');

    if (authButtons){
        if (data.is_authenticated){
            let librarianMenu = '';
            let adminMenu = '';
            if (data.role === 'librarian'){
                librarianMenu = `
                  <li class="header--menu--list--li">
                      <a href="/exhibitions" class="header--menu--list--li">Конструктор выставки</a>
                  </li>
                  <li class="header--menu--list--li">
                      <a href="/books" class="header--menu--list--li">Конструктор книги</a>
                  </li>`;
            }
            else if (data.role === 'admin'){
                adminMenu = `
                <li class="header--menu--list--li">
                      <a href="admin/dashboard" class="header--menu--list--l">Админ панель</a>
                </li>
                `;
            }
            authButtons.innerHTML = `
                <li class="header--menu--list--li"><a href="/">Главная</a></li>
                ${librarianMenu}
                ${adminMenu}
                <li class="header--menu--list--li"><a href="/users/logout" class="logout-button">Выйти</a></li>
`;
        } else{
            authButtons.innerHTML = `
                <li class="header--menu--list--li"><a href="/">Главная</a></li>
                <a href="/user-login/" class="header--menu--list--li"">Вход</a>
                <a href="/user-regit/" class="header--menu--list--li"">Регистрация</a>
            `;}
        }
    }catch (error){
        console.error("Ошибка обновления меню: ", error);
    }
}