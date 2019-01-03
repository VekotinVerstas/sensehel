import React, { Component } from 'react';
import './home.styles.css';
import AppHeader from '../../components/AppHeader';
import SensorValueCard from '../../components/SensorValueCard';
import Icons from '../../assets/Icons';

const mockSubscriptions = [
  {
    title: 'Temperature',
    icon: Icons.Temperature_Normal,
    value: 23,
    unit: '℃',
    lastUpdated: '20 seconds ago'
  },
  {
    title: 'Humidity',
    icon: Icons.Humidity_Normal,
    value: 40,
    unit: '%',
    lastUpdated: '10 min ago'
  },
  {
    title: 'Carbon Dioxide',
    icon: Icons.CO2_Normal,
    value: 300,
    unit: 'ppm',
    lastUpdated: '40 min ago'
  }
];

class HomePage extends Component {
  state = {
    refreshing: false
  };

  render() {
    const { refreshing } = this.state;

    return (
      <div className="home-page">
        <AppHeader
          headline="PAULI TOIVONEN"
          title={`URHO KEKKOSEN KATU 7B,\nHELSINKI`}
          hasBgImage
        />

        <div className="home-page__cards-container tab-page__content">
          {mockSubscriptions.map(s => (
            <SensorValueCard
              key={s.title}
              title={s.title}
              icon={s.icon}
              value={s.value}
              unit={s.unit}
              lastUpdated={s.lastUpdated}
              refreshing={refreshing}
            />
          ))}
        </div>
      </div>
    );
  }
}

export default HomePage;
