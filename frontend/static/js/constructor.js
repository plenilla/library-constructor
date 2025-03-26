
let currentSectionIdForBook = null; 


async function loadSectionsAndContents() {
const [sectionsResponse, contentsResponse, booksResponse] = await Promise.all([
		fetch('http://localhost:8000/page/sections'),
		fetch('http://localhost:8000/page/contents/'),
		fetch('http://localhost:8000/page/books/')
]);

const [sections, contents, books] = await Promise.all([
		sectionsResponse.json(),
		contentsResponse.json(),
		booksResponse.json()
]);

const sectionsList = document.getElementById('sectionsList');
sectionsList.innerHTML = sections.map(section => {
		const sectionContents = contents.filter(content => content.section_id == section.id);
		let contentHtml = '';

		sectionContents.forEach(content => {
				const book = books.find(book => book.id === content.books_id); // Находим книгу по ID
				const textData = content.text_data?.text_data || '';

				contentHtml += `
						<li class="content-item" data-id="${content.id}">
								${textData ? `
										<span class="content-text" data-text-id="${content.text_data.id}">
												${textData}
										</span>
								` : ''}

								${book ? `
										<div class="book-content">
												<img src="http://localhost:8000${book.image}" alt="${book.title}">
												<div>
														<h3>${book.title}</h3>
														<p>${book.description}</p>
												</div>
										</div>
								` : ''}

								<button class="delete-content-btn button">Удалить</button>
						</li>
				`;
		});

		return `
			<li class="section-item" data-id="${section.id}">
				<span class="section-title"><h2>${section.title}</h2></span>
				<button class="edit-btn button">edit</button>
				<button class="delete-btn button">delete</button>
				<button class="add-text-btn button">add-text</button>
				<button class="add-img-btn button">add-image</button>
				<button class="add-book-btn button" data-section-id="${section.id}">Добавить книгу</button>
				<ul class="contentsList" style="list-style-type: none; padding: 0;">
					${contentHtml}
				</ul>
			</li>
		`;
}).join('');

document.querySelectorAll('.edit-btn').forEach(btn => {
		btn.addEventListener('click', handleEditClick);
});
document.querySelectorAll('.delete-btn').forEach(btn => {
		btn.addEventListener('click', handleDeleteClick);
});
document.querySelectorAll('.add-text-btn').forEach(btn => {
		btn.addEventListener('click', handleAddContentClick);
});
document.querySelectorAll('.add-img-btn').forEach(btn => {
		btn.addEventListener('click', handleAddImageBookClick);
});
document.querySelectorAll('.delete-content-btn').forEach(btn => {
		btn.addEventListener('click', handleDeleteContent);
});
document.querySelectorAll('.add-book-btn').forEach(btn => {
		btn.addEventListener('click', handleAddBook);
});
}

async function loadBooks() {
const booksResponse = await fetch('http://localhost:8000/page/books/');
const books = await booksResponse.json();

const bookSelect = document.getElementById('bookSelect');
bookSelect.innerHTML = ''; // Очистить список перед добавлением новых элементов

books.forEach(book => {
		const option = document.createElement('option');
		option.value = book.id; // 
		option.textContent = book.title;
		bookSelect.appendChild(option);
});
}

async function handleAddBook(event) {
currentSectionIdForBook = event.target.dataset.sectionId;
console.log(currentSectionIdForBook); // теперь должно выводиться корректное значение
await loadBooks(); // Загружаем список книг в select
document.getElementById('modalBookAddContent').style.display = 'flex';
}

// Обработчик сохранения выбранной книги
document.getElementById('modalBookSaveContent').addEventListener('click', async () => {
// Получаем выбранное значение из select
const selectedBookId = document.getElementById('bookSelect').value;
console.log("Выбранное значение bookId:", selectedBookId);
console.log("currentSectionIdForBook:", currentSectionIdForBook);

if (!selectedBookId || !currentSectionIdForBook) {
alert('Пожалуйста, выберите книгу!');
return;
}

try {
const response = await fetch('http://localhost:8000/page/contents/', {
	method: 'POST',
	headers: { 'Content-Type': 'application/json' },
	body: JSON.stringify({
			section_id: parseInt(currentSectionIdForBook),
			books_id: parseInt(selectedBookId) // Используем имя поля, как определено в модели
	})
});

if (!response.ok) throw new Error('Ошибка сервера при привязке книги');

const result = await response.json();
console.log('Книга успешно связана с контентом:', result);

// Закрываем модальное окно и обновляем список
document.getElementById('modalBookAddContent').style.display = 'none';
document.getElementById('bookSelect').value = '';
loadSectionsAndContents();
} catch (error) {
console.error('Ошибка:', error);
alert('Ошибка при привязке книги');
}
});


// Обработчик закрытия модального окна
document.getElementById('modalBookCancelContent').addEventListener('click', () => {
document.getElementById('modalBookAddContent').style.display = 'none';
document.getElementById('bookSelect').value = ''; // Очищаем выбранное значение
});










async function handleAddImageBookClick(event) {
	// Открываем модальное окно
	document.getElementById('modalBook').style.display = 'flex';
}

// Закрытие модального окна
document.getElementById('modalBookCancel').addEventListener('click', () => {
	document.getElementById('modalBook').style.display = 'none';
});

document.getElementById('modalBookSave').addEventListener('click', async () => {
	const title = document.getElementById('bookTitle').value;
	const description = document.getElementById('bookDescription').value;
	const imageFile = document.getElementById('bookImageUrl').files[0];

	if (!title || !description || !imageFile) {
		alert('Заполните все поля!');
		return;
	}

	// Собираем данные в FormData, чтобы передать файл
	const formData = new FormData();
	formData.append('title', title);
	formData.append('description', description);
	formData.append('image', imageFile);

	try {
		const response = await fetch('http://localhost:8000/page/books/', {
			method: 'POST',
			body: formData  // Заголовок Content-Type не устанавливается вручную
		});

		if (!response.ok) throw new Error('Ошибка сервера при добавлении книги');

		const newBook = await response.json();
		console.log('Книга успешно добавлена:', newBook);

		// Если требуется связать новую книгу с разделом,
		// можно вызвать дополнительный запрос после успешного создания книги
		if (currentSectionIdForBook) {
			await bindBookToContent(currentSectionIdForBook, newBook.id);
		}

		// Закрываем модальное окно и обновляем список
		document.getElementById('modalBook').style.display = 'none';
		loadSectionsAndContents();
	} catch (error) {
		console.error('Ошибка:', error);
		alert(error.message);
	}
});


async function createSections() {
	const titleSections = document.getElementById('titleSections').value;
	await fetch('http://localhost:8000/page/sections', {
		method: 'POST',
		headers: {'Content-Type': 'application/json'},
		body: JSON.stringify({ title: titleSections })
	});
	loadSectionsAndContents();
	document.getElementById('titleSections').value = '';
}

async function updateSection(id, newTitle) {
	const response = await fetch(`http://localhost:8000/page/sections/${id}`, {
		method: 'PUT',
		headers: {'Content-Type': 'application/json'},
		body: JSON.stringify({ title: newTitle })
	});
	location.reload();
	return await response.json();
}

function handleEditClick(event) {
	const li = event.target.closest('li');
	const sectionId = li.dataset.id;
	const titleElement = li.querySelector('.section-title');
	let input = li.querySelector('input');
	
	if (event.target.textContent === 'edit') {
		input = document.createElement('input');
		input.value = titleElement.textContent;
		titleElement.replaceWith(input);
		event.target.textContent = 'save';
	} else {
		const newTitle = input.value;
		updateSection(sectionId, newTitle).then(() => {
			titleElement.textContent = newTitle;
			input.replaceWith(titleElement);
			event.target.textContent = 'edit';
		});
	}
}

async function deleteSections(id) {
	await fetch(`http://localhost:8000/page/sections/${id}`, {
		method: 'DELETE',
		headers: {'Content-Type': 'application/json'},
	});
}

function handleDeleteClick(event) {
	const li = event.target.closest('li');
	const sectionId = li.dataset.id;
	if (confirm("Вы уверены, что хотите удалить этот раздел?")) {
		deleteSections(sectionId);
	}
}


async function handleAddContentClick(event) {
	const sectionItem = event.target.closest('.section-item');
	const sectionId = sectionItem.getAttribute('data-id');
	const userText = prompt("Введите текст для нового контента:");
	if (!userText) return;
	
	const textResponse = await fetch('http://localhost:8000/page/textForcontent/', {
		method: 'POST',
		headers: {'Content-Type': 'application/json'},
		body: JSON.stringify({ text_data: userText })
	});
	const newText = await textResponse.json();
	
	await fetch('http://localhost:8000/page/contents/', {
		method: 'POST',
		headers: {'Content-Type': 'application/json'},
		body: JSON.stringify({ section_id: parseInt(sectionId), text_id: newText.id })
	});
	loadSectionsAndContents();
}



async function handleDeleteContent(event) {
	const contentItem = event.target.closest('.content-item');
	const contentId = contentItem.getAttribute('data-id');
	if (!confirm("Вы уверены, что хотите удалить этот контент?")) return;
	
	await fetch(`http://localhost:8000/page/contents/${contentId}`, {
		method: 'DELETE',
		headers: { 'Content-Type': 'application/json' }
	});
	loadSectionsAndContents();
}

async function updateTextContent(textId, newText) {
	const response = await fetch(`http://localhost:8000/page/textForcontent/${textId}`, {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ text_data: newText })
	});
	const updatedContent = await response.json();
	console.log('Updated content:', updatedContent);
	return updatedContent;
}



function handleEditTextClick(event) {
	const contentItem = event.target.closest('.content-item');
	const textElement = contentItem.querySelector('.content-text');
	const textId = textElement.dataset.textId;
	const input = contentItem.querySelector('.editing-input');
	
	if (event.target.textContent === 'update-text') {
		input.value = textElement.textContent.trim();
		textElement.classList.add('hidden');
		input.classList.add('visible');
		event.target.textContent = 'save';
	} else {
		const newText = input.value;
		updateTextContent(textId, newText).then(updatedContent => {
			input.classList.remove('visible');
			input.classList.add('hidden');
			const updatedTextElement = document.createElement('span');
			updatedTextElement.textContent = updatedContent.text_data.text_data;
			updatedTextElement.classList.add('content-text');
			updatedTextElement.dataset.textId = updatedContent.text_data.id;
			input.replaceWith(updatedTextElement);
			event.target.textContent = 'update-text';
			loadSectionsAndContents();
		});
	}
}



document.getElementById('createSections').addEventListener('click', createSections);
document.addEventListener('DOMContentLoaded', loadSectionsAndContents);
console.log(currentSectionIdForBook);