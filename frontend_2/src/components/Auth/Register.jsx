import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Auth.module.css'

export default function Register() {
    const [formData, setFormData] = useState({
      username: '',
      password: '',
      password_confirm: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      setError('');
  
      if (formData.password !== formData.password_confirm) {
        setError('Пароли не совпадают');
        return;
      }
  
      try {
        setIsLoading(true);
        
        // Создаем FormData объект
        const formDataToSend = new FormData();
        formDataToSend.append('username', formData.username);
        formDataToSend.append('password', formData.password);
        formDataToSend.append('password_confirm', formData.password_confirm);
  
        const response = await fetch('http://localhost:8000/users/register', {
          method: 'POST',
          body: formDataToSend, // Отправляем как form-data
        });
  
        if (response.redirected) {
          // Обрабатываем редирект от сервера
          window.location.href = response.url;
          return;
        }
  
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Ошибка регистрации');
        }
  
        navigate('/user-login/');
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
  
    const handleChange = (e) => {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value
      });
    };
	return (
		<div className={styles.container}>
			<form onSubmit={handleSubmit}>
				<h1>Регистрация</h1>
				{error && <div className={styles.errorMessage}>{error}</div>}

				<input
					type='text'
					id='username'
					name='username'
					placeholder='Введите логин'
					value={formData.username}
					onChange={handleChange}
					required
				/>

				<input
					type='password'
					id='password'
					name='password'
					placeholder='Введите пароль'
					value={formData.password}
					onChange={handleChange}
					required
				/>

				<input
					type='password'
					id='password_confirm'
					name='password_confirm'
					placeholder='Подтвердите пароль'
					value={formData.password_confirm}
					onChange={handleChange}
					required
				/>

				<button type='submit' disabled={isLoading}>
					{isLoading ? 'Загрузка...' : 'Зарегистрироваться'}
				</button>
			</form>

			<div className={styles.forgot}>
				<span>Если есть аккаунт</span>
				<a href='/user-login'>Авторизоваться</a>
			</div>
		</div>
	);
};