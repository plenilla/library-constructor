import "./Contens.css"

export default function Contents(){
	return(
		<div id="main__content" className="main">
			<div className="main__container">
				<div className="exhibition__column">
					<h1>Электронные книжные выставки</h1>
					<div id="exhibitionsContainer" className="exhibition__main"></div>
				</div>
			</div>
		</div>
	)
}