import React, { useState, useContext } from "react";
import { Link } from "react-router-dom";

import "./Sidebar.css";

import logo from "../../assets/images/logo.png";

import { AuthContext } from "../../contexts/AuthContext";

import SidebarItem from "./SidebarItem";

import { sidebar_teacher, sidebar_student } from "../../helpers/sidebar.items";

const Sidebar = props => {
	const { loggedIn } = useContext(AuthContext);
	const [isCollapsed, setIsCollapsed] = useState(false);

	let currentSidebar;

	if (loggedIn.role === "teacher") {
		currentSidebar = sidebar_teacher;
	} else if (loggedIn.role === "student") {
		currentSidebar = sidebar_student;
	}

	const activeItem =
		loggedIn.role && currentSidebar.findIndex(item => item.route === window.location.pathname);

	function closeNav() {
		setIsCollapsed(true);
		document.getElementById("mySidebar").style.width = "80px";
		document.getElementById("main").style.paddingLeft = "80px";
	}

	function openNav() {
		setIsCollapsed(false);
		document.getElementById("mySidebar").style.width = "300px";

		window.matchMedia("(max-width: 800px)").matches
			? (document.getElementById("main").style.paddingLeft = "80px")
			: (document.getElementById("main").style.paddingLeft = "300px");
	}

	return (
		<>
			{loggedIn.role ? (
				<div id="mySidebar" className="sidebar">
					{isCollapsed === true ? (
						<div className="sidebar__itemmenu">
							<button className="sidebar__item-inner" onClick={openNav}>
								<i className="bx bx-menu"></i>
							</button>
						</div>
					) : (
						<div className="sidebar__itemmenu">
							<button className="sidebar__item-inner" onClick={closeNav}>
								<i className="bx bx-menu"></i>
							</button>
						</div>
					)}

					<div className="sidebar__logo">
						<img src={logo} alt="company logo" />
					</div>

					{currentSidebar.map((item, index) =>
						item.display_name !== "Sign Out" ? (
							<Link to={item.route} key={index}>
								{isCollapsed === true ? (
									<SidebarItem icon={item.icon} active={index === activeItem} />
								) : (
									<SidebarItem
										title={item.display_name}
										icon={item.icon}
										active={index === activeItem}
									/>
								)}
							</Link>
						) : (
							<Link
								to={"#"}
								onClick={() => {
									if (window.confirm("Are you really want to sign out?")) {
										localStorage.clear();
										window.location = "/";
										return;
									}
								}}
								key={index}
							>
								{isCollapsed === true ? (
									<SidebarItem icon={item.icon} active={index === activeItem} />
								) : (
									<SidebarItem
										title={item.display_name}
										icon={item.icon}
										active={index === activeItem}
									/>
								)}
							</Link>
						)
					)}
				</div>
			) : (
				""
			)}
		</>
	);
};

export default Sidebar;
