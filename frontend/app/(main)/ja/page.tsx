"use client"
import React, { useState, useEffect } from 'react';
import useMyAxios from '@/composables/useMyAxios';
import { Modal } from '@/components/ui/modal'; 
import Image from 'next/image';
import BackButton from '@/components/Mybuttons/BackButton';

interface Author {
  id: number;
  name: string;
}

interface Genre {
  id: number;
  name: string;
}

const AuthorsAndGenresPage = () => {
  const [authors, setAuthors] = useState<Author[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);
  const [newAuthorName, setNewAuthorName] = useState('');
  const [newGenreName, setNewGenreName] = useState('');
  
  // Состояния для управления модальным окном
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<{
    type: 'author' | 'genre';
    id: number;
    name: string;
  } | null>(null);
  const [editName, setEditName] = useState('');

  const { request: fetchRequest } = useMyAxios();
  const { request: createRequest } = useMyAxios();
  const { request: deleteRequest } = useMyAxios();
  const { request: updateRequest } = useMyAxios();

  useEffect(() => {
    const fetchAuthorsAndGenres = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [authorsResponse, genresResponse] = await Promise.all([
          fetchRequest('v2/library/authors/', 'GET'),
          fetchRequest('v2/library/genres/', 'GET')
        ]);
        
        setAuthors(authorsResponse.data);
        setGenres(genresResponse.data);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAuthorsAndGenres();
  }, []);

  // Открытие модального окна для редактирования
  const openEditModal = (type: 'author' | 'genre', id: number, currentName: string) => {
    setEditingItem({ type, id, name: currentName });
    setEditName(currentName);
    setIsModalOpen(true);
  };

  // Закрытие модального окна
  const closeModal = () => {
    setIsModalOpen(false);
    setEditingItem(null);
    setEditName('');
  };

  // Обработка обновления элемента
  const handleUpdateItem = async () => {
    if (!editingItem || !editName.trim()) return;

    try {
      const url = editingItem.type === 'author' 
        ? `v2/library/authors/${editingItem.id}/` 
        : `v2/library/genres/${editingItem.id}/`;
      
      const response = await updateRequest(
        url, 
        'PUT', 
        { name: editName }
      );

      if (editingItem.type === 'author') {
        setAuthors(authors.map(a => 
          a.id === editingItem.id ? { ...a, name: editName } : a
        ));
      } else {
        setGenres(genres.map(g => 
          g.id === editingItem.id ? { ...g, name: editName } : g
        ));
      }

      closeModal();
    } catch (error) {
      console.error('Error updating item:', error);
      alert('Failed to update');
    }
  };

  const handleAddAuthor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAuthorName.trim()) return;
    
    try {
      const response = await createRequest(
        'v2/library/authors/', 
        'POST', 
        { name: newAuthorName }
      );
      
      setAuthors([...authors, response.data]);
      setNewAuthorName('');
    } catch (error) {
      console.error('Error adding author:', error);
      alert('Failed to add author');
    }
  };

  const handleAddGenre = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGenreName.trim()) return;
    
    try {
      const response = await createRequest(
        'v2/library/genres/', 
        'POST', 
        { name: newGenreName }
      );
      
      setGenres([...genres, response.data]);
      setNewGenreName('');
    } catch (error) {
      console.error('Error adding genre:', error);
      alert('Failed to add genre');
    }
  };

  const handleDeleteAuthor = async (authorId: number) => {
    if (!window.confirm('Are you sure you want to delete this author?')) return;
    
    try {
      await deleteRequest(`v2/library/authors/${authorId}/`, 'DELETE');
      setAuthors(authors.filter((author) => author.id !== authorId));
    } catch (error) {
      console.error('Error deleting author:', error);
      alert('Failed to delete author');
    }
  };

  const handleDeleteGenre = async (genreId: number) => {
    if (!window.confirm('Are you sure you want to delete this genre?')) return;
    
    try {
      await deleteRequest(`v2/library/genres/${genreId}/`, 'DELETE');
      setGenres(genres.filter((genre) => genre.id !== genreId));
    } catch (error) {
      console.error('Error deleting genre:', error);
      alert('Failed to delete genre');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="text-red-500">Error: {error}</div>
        <button 
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded"
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  const iconSize = 20
  return (
    <>
    <BackButton
        className='relative p-0 m-0'
      ></BackButton>
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Авторы и формы произведения</h1>
      
      {/* Authors Section */}
      <section className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Авторы</h2>
        </div>

        <form onSubmit={handleAddAuthor} className="mb-4 flex gap-2">
          <input
            type="text"
            value={newAuthorName}
            onChange={(e) => setNewAuthorName(e.target.value)}
            placeholder="Введите названия автора"
            className="border rounded px-3 py-1 flex-grow"
          />
          <button 
            type="submit"
            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-700"
            title="Создать автора"
          >
            <Image
              src='/icons/add.svg'
              alt='Добавить автора'
              width={iconSize}
              height={iconSize}
              className="filter brightness-0 invert"
            />
          </button>
        </form>
        
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse border border-black">
            <thead>
              <tr className="bg-black text-white">
                <th className="border border-gray-300 px-4 py-2">ID</th>
                <th className="border border-gray-300 px-4 py-2">Name</th>
                <th className="border border-gray-300 px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {authors.map((author) => (
                <tr key={author.id} className="bg-white">
                  <td className="border border-gray-300 px-4 py-2 text-center">{author.id}</td>
                  <td className="border border-gray-300 px-4 py-2">{author.name}</td>
                  <td className="border border-gray-300 px-4 py-2 text-center space-x-2">
                    <button
                      onClick={() => openEditModal('author', author.id, author.name)}
                      className="p-1 rounded transition-transform duration-200 hover:scale-110 group relative"
                      title="Редактировать"
                    >
                      <Image
                        src='/icons/rewrite.svg'
                        alt='Изменить имя автора'
                        width={iconSize}
                        height={iconSize}
                      />
                    </button>
                    <button
                      onClick={() => handleDeleteAuthor(author.id)}
                      className="p-1 rounded transition-transform duration-200 hover:scale-110 group relative"
                      title="Удалить"
                    >
                      <Image
                        src='/icons/delete.svg'
                        alt='Удалить'
                        width={iconSize}
                        height={iconSize}
                      />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Genres Section */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Формы произведения</h2>
        </div>

        <form onSubmit={handleAddGenre} className="mb-4 flex gap-2">
          <input
            type="text"
            value={newGenreName}
            onChange={(e) => setNewGenreName(e.target.value)}
            placeholder="Введите название формы произведения"
            className="border rounded px-3 py-1 flex-grow"
          />
          <button 
            type="submit"
            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-700"
            title="Создать форму произведения"
          >
            <Image
              src='/icons/add.svg'
              alt='Добавить форму произведения'
              width={iconSize}
              height={iconSize}
              className="filter brightness-0 invert"
            />
          </button>
        </form>
        
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-black text-white">
                <th className="border border-gray-300 px-4 py-2">ID</th>
                <th className="border border-gray-300 px-4 py-2">Name</th>
                <th className="border border-gray-300 px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {genres.map((genre) => (
                <tr key={genre.id} className="bg-white">
                  <td className="border border-gray-300 px-4 py-2 text-center">{genre.id}</td>
                  <td className="border border-gray-300 px-4 py-2">{genre.name}</td>
                  <td className="border border-gray-300 px-4 py-2 text-center space-x-2">
                    <button
                      onClick={() => openEditModal('genre', genre.id, genre.name)}
                      className="p-1 rounded transition-transform duration-200 hover:scale-110 group relative"
                      title="Редактировать"
                    >
                      <Image
                        src='/icons/rewrite.svg'
                        alt='Изменить жанр'
                        width={iconSize}
                        height={iconSize}
                      />
                    </button>
                    <button
                      className="p-1 rounded transition-transform duration-200 hover:scale-110 group relative"
                      title="Удалить"
                      onClick={() => handleDeleteGenre(genre.id)}
                    >
                      <Image
                        src='/icons/delete.svg'
                        alt='Удалить'
                        width={iconSize}
                        height={iconSize}
                      />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Модальное окно редактирования */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingItem ? `Edit ${editingItem.type === 'author' ? 'Author' : 'Genre'}` : ''}
        actions={
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={closeModal}
              className="px-4 py-2 border rounded hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleUpdateItem}
              disabled={!editName.trim()}
              className={`px-4 py-2 bg-blue-500 text-white rounded ${
                !editName.trim() ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'
              }`}
            >
              Save
            </button>
          </div>
        }
        size="md"
        showCloseButton={true}
      >
        {editingItem && (
          <div className="p-4">
            <label className="block mb-2 font-medium">
              {editingItem.type === 'author' ? 'Author Name' : 'Genre Name'}
            </label>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={`Enter ${editingItem.type} name`}
            />
          </div>
        )}
      </Modal>
    </div>
    </>
  );
};

export default AuthorsAndGenresPage;