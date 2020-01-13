import React from 'react';
import '../Card/card.styles.css';
import './subscribedservicecard.styles.css';
import BottomButton from '../BottomButton';

const SubscribedServiceCard = ({
  logo,
  title,
  url
}) => (
  <div className="card">
    <div className="card__row">
      <div className="card__col1">
        <img src={logo} className="service-logo" alt="service" />
      </div>

      <div className="card__col2">
        <p className="headline card__text">{title}</p>
      </div>

      <div className="card__col3" />
    </div>
    <iframe src={url} height={320} width="100%" />
    <BottomButton
      onClick={() => {
        window.open(url);
      }}
      title="Go to service"
    />
  </div>
);

export default SubscribedServiceCard;
