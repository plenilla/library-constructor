import React from 'react'
import useAuth from '../../hooks/useAuth'
import styles from './Headers.module.css'
import {Link} from 'react-router-dom'

export default function Header() {
	const isAuthenticated = useAuth()

	return (
		<header className={styles.header}>
			<nav className={styles.headerMenu}>
				<div className={styles.headerMenuIcon}></div>
				<ul className={styles.headerMenuList}>
					<li className={styles.headerMenuListItem}>
						<a href='/'>Главная</a>
					</li>
					{isAuthenticated ? (
						<li className={styles.headerMenuListItem}>
							<a href='/users/logout' className={styles.logoutBut}></a>
						</li>
					) : (
						<>
							<li className={styles.headerMenuListItem}>
								<a href='/'>Вход</a>
							</li>
							<li className={styles.headerMenuListItem}>
								<Link to="/register">Регистрация</Link>
							</li>
						</>
					)}
				</ul>
			</nav>
		</header>
	)
}
