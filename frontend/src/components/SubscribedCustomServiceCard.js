import React from 'react';
import './Card/card.styles.css';
import './SubscribedServiceCard/subscribedservicecard.styles.css';
import BottomButton from './BottomButton';

const SubscribedServiceCard = ({subscription}) => {
  const {img_logo_url, service, report_url, preview_url} = subscription;

  return <div className="card">
    <div className="card__row">
      <div className="card__col1">
        <img src={img_logo_url} className="service-logo" alt="service"/>
      </div>

      <div className="card__col2">
        <p className="headline card__text">{service}</p>
      </div>

      <div className="card__col3"/>
    </div>
    <iframe src={preview_url} height={340} width="100%"/>
    <BottomButton
      onClick={() => {
        window.open(report_url);
      }}
      title="Go to service"
    />
  </div>
}

export default SubscribedServiceCard;
