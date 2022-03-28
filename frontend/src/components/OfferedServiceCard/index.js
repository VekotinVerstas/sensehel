import React from 'react';
import './offeredservicecard.styles.css';
import ServiceSubscription from './ServiceSubscription';
import Card from '../Card';
import '../Card/card.styles.css';

const OfferedServiceCard = ({
  service,
  subscribed,
  handleSubscribe,
  handleUnsubscribe
}) => {
  const {
    img_logo_url: logoUrl,
    img_service_url: serviceImageUrl,
    name,
    description,
  } = service;

  return (
    <div>
      <Card image={logoUrl} name={name} description={description} CollapsibleComponent={
          <>
            <img className="service-image" src={serviceImageUrl} alt="placeholder" />
            <ServiceSubscription {...{service, subscribed, handleSubscribe, handleUnsubscribe}} />
          </>
        }
      />
    </div>
  );
};
export default OfferedServiceCard;
