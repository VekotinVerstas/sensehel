import React from 'react';
import CircularProgress from '@material-ui/core/CircularProgress/CircularProgress';
import './sensorvaluecard.styles.css';

const SensorValueCard = ({
  title,
  icon,
  unit,
  value,
  lastUpdated,
  refreshing
}) => (
  <div className="service-card">
    {!refreshing ? (
      <div>
        <img className="service-card__header__icon" src={icon} alt={title} />
        <span className="large-number" style={{ margin: '0 4px 0 8px' }}>
          {value}
          <span className="number">{unit}</span>
        </span>
        <span className="small-body"> {lastUpdated}</span>
      </div>
    ) : (
      <CircularProgress className="service-card__spinner" />
    )}
  </div>
);

export default SensorValueCard;
