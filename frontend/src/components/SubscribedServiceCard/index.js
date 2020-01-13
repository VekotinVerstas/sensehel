import React from 'react';
import '../Card/card.styles.css';
import './subscribedservicecard.styles.css';
import BottomButton from '../BottomButton';

const subscriptionUrl = (baseUrl, subscription) => `${baseUrl}?subscription=${subscription.uuid}`;

const SubscribedServiceCard = ({subscription}) => {
  const {img_logo_url, name, report_url, preview_url} = subscription.service;

  return <div className="card">
    <div className="card__row">
      <div className="card__col1">
        <img src={img_logo_url} className="service-logo" alt="service"/>
      </div>

      <div className="card__col2">
        <p className="headline card__text">{name}</p>
      </div>

      <div className="card__col3"/>
    </div>
    <iframe src={subscriptionUrl(preview_url, subscription)} height={320} width="100%"/>
    <BottomButton
      onClick={() => {
        window.open(subscriptionUrl(report_url, subscription));
      }}
      title="Go to service"
    />
  </div>
}

export default SubscribedServiceCard;
