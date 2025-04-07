// App.jsx
import React from 'react'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import './App.css'
import Register from './components/Auth/Register'
import Contents from './components/Contents/Contens'
import Footer from './components/Footer/Footer'
import Header from './components/Headers/Headers'

export default function App() {
	return (
		<Router>
			<Routes>
				<Route
					path='/'
					element={
						<>
							<Header />
							<main>
								<Contents />
							</main>
							<Footer />
						</>
					}
				/>
				<Route path='/register' element={<Register />} />
			</Routes>
		</Router>
	)
}
