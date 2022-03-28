import React, { Component } from 'react';
import './tabs.styles.css';
import Icons from '../../assets/Icons';
import HomePage from '../Home';
import SubscriptionsPage from '../Subscriptions';
import SensorsPage from '../Sensors';
import Images from "assets/Images";
import API from "services/Api";
import ConfirmDialog from "components/ConfirmDialog";
import * as PropTypes from "prop-types";

const tabOptions = [
  {
    name: 'home',
    component: changeTab => <HomePage changeTab={changeTab} />,
    icon: Icons.Home_Icon,
    activeIcon: Icons.Home_Icon_Active
  },
  {
    name: 'subscriptions',
    component: () => <SubscriptionsPage />,
    icon: Icons.Subscription_Icon,
    activeIcon: Icons.Subscription_Icon_Active
  },
  {
    name: 'sensors',
    component: () => <SensorsPage />,
    icon: Icons.Sensors_Icon,
    activeIcon: Icons.Sensors_Icon_Active
  }
];

class Tabs extends Component {
  state = {
    activeTab: tabOptions[0]
  };

  onTabChange = selectedTabIndex => {
    const selectedTab = tabOptions[selectedTabIndex];
    this.setState({ activeTab: selectedTab });
  };

  render() {
    const { activeTab} = this.state;

    return (
      <div className="tabs-page">
        <div className="tabs-page__page">
          {activeTab.component(this.onTabChange)}
        </div>

        <BottomTabNavigator
          tabs={tabOptions}
          activeTab={activeTab}
          onTabChange={this.onTabChange}
        />
      </div>
    );
  }
}

class BottomTabNavigator extends Component {
  state = {
    logoutConfirmOpen: false
  };

  onLogout = () => {
    this.setState({ logoutConfirmOpen: true });
  };

  handleLogout = () => {
    localStorage.clear();
    API.setToken('');
    window.location.reload()
  };

  onCloseConfirm = () => {
    this.setState({ logoutConfirmOpen: false});
  };

  render() {
    const {tabs, activeTab, onTabChange} = this.props;
    const {logoutConfirmOpen} = this.state;

    return (
      <div className="bottom-tab-navigator">
        {tabs.map((t, i) => (
          <div className="icon-container" key={t.name}>
            <img
              className="icon-container__img"
              src={activeTab.name === t.name ? t.activeIcon : t.icon}
              onClick={() => onTabChange(i)}
              alt={t.name}
              onKeyDown={() => this.onTabChange(i)}
            />
          </div>
        ))}
        <div className="icon-container">
          <img
            className="icon-container__img"
            src={Icons.Logout_Icon}
            onClick={() => this.onLogout()}
            alt="Log out"
          />
        </div>
        <ConfirmDialog
          title="Are you sure you want to logout?"
          description="You will be redirected to login screen"
          handleConfirm={this.handleLogout}
          open={logoutConfirmOpen}
          handleClose={this.onCloseConfirm}
        />
      </div>
    );
  }
}

BottomTabNavigator.propTypes = {
  tabs: PropTypes.any,
  activeTab: PropTypes.any,
  onTabChange: PropTypes.any
}

export default Tabs;
