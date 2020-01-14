import React, { Component } from 'react';
import './sensors.styles.css';
import AppHeader from '../../components/AppHeader';
import SensorListCard from '../../components/SensorListCard';
import API from '../../services/Api';
import CustomizedSnackbar from '../../components/Snackbar';
import SensorConfig from '../../config/SensorConfig';

class SensorsPage extends Component {
  state = {
    sensors: [],
    errorMessage: ''
  };

  async componentWillMount() {
    try {
      const sensors = await API.getSensorValues();

      this.setState({ sensors });
    } catch (e) {
      this.setState({
        errorMessage: {
          title: 'Could not fetch apartment sensors',
          subtitle: `${e.message}`
        }
      });
    }
  }

  render() {
    const { sensors, errorMessage } = this.state;

    return (
      <div className="sensors-page">
        <AppHeader headline="MY SENSORS" title="DEVICES INFORMATION" />

        <div className="sensors-page__content tab-page__content">
          {sensors.map(sensor => {
            const sensorConfig =
              SensorConfig[sensor.uiType] || SensorConfig.DEFAULT;
            return (
              <SensorListCard
                key={sensor.id}
                icon={sensorConfig.icon}
                name={sensor.name}
                description={sensor.description}
                identifier={sensor.identifier}
              />
            );
          })}
        </div>

        <CustomizedSnackbar
          message={errorMessage}
          variant="error"
          handleClose={() => this.setState({ errorMessage: '' })}
          open={!!errorMessage}
        />
      </div>
    );
  }
}

export default SensorsPage;
