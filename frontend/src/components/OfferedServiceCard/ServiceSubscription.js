import _ from 'lodash';
import React, {Component} from 'react';
import API from "services/Api";
import Checkbox from "@material-ui/core/Checkbox/Checkbox";
import FormControlLabel from "@material-ui/core/FormControlLabel/FormControlLabel";
import BottomButton from '../BottomButton';
import CheckboxesSection from './CheckboxesSection';
import ConfirmDialog from '../ConfirmDialog';

class ServiceSubscription extends Component {
  state = {
    consentChecked: false,
    confirmOpen: false,
    requesting: false,
    apartment: undefined,
    selectedAttributes: [],
    includeHistory: false
  };

  componentDidMount() {
    API.getApartment().then((apartment) => this.setState({apartment}))
  }

  handleCheckChange = value => {
    this.setState({[value]: !this.state[value]}); // eslint-disable-line
  };

  onRequest = async requestHandler => {
    this.setState({requesting: true, confirmOpen: false});
    await requestHandler();
    this.setState({requesting: false});
  };

  onUnsubscribeClick = () => this.setState({confirmOpen: true});

  render() {
    const {service, subscribed, handleSubscribe, handleUnsubscribe, classes} = this.props;
    const {consentChecked, selectedAttributes, confirmOpen, requesting, apartment, includeHistory} = this.state;
    const sensorAttributes = this.getSensorAttributes();

    let buttonTitle = 'subscribe';
    if (requesting) {
      buttonTitle = 'requesting...';
    } else if (subscribed) {
      buttonTitle = 'unsubscribe';
    }

    return (
      <>
        <div className="offered-service-card__detail-container">
          {sensorAttributes.length &&
            <div className="card-section">
              <h5 className="subheader">Select data to share with service:</h5>
              {sensorAttributes.map((attr) => {
                const checked = selectedAttributes.includes(attr.id);
                return <p key={attr.id}><FormControlLabel
                  control={
                    <Checkbox
                      checked={checked}
                      onChange={() => {
                        const newSelection = checked
                          ? _.without(selectedAttributes, attr.id)
                          : selectedAttributes.concat(attr.id);
                        this.setState({selectedAttributes: newSelection})
                      }}
                    />
                  }
                  label={
                    <span className="body-text">
                      {attr.description}<br/>Sensor {attr.sensor.identifier}<br/>{apartment.street}
                    </span>}
                /></p>
              })}
              <FormControlLabel
                control={
                  <Checkbox
                    checked={includeHistory}
                    onChange={() => this.setState({includeHistory: !includeHistory})}
                  />
                }
                label={
                  <span className="body-text">Also share past data</span>}
              />
            </div>
          }
          <hr/>
          <CheckboxesSection
            consentChecked={subscribed || consentChecked}
            handleChange={this.handleCheckChange}
            classes={classes}
            disabled={subscribed}
            termsAndConditions={service.eula_url}
          />
        </div>

        <BottomButton
          variant={subscribed ? 'negative' : 'default'}
          title={buttonTitle}
          onClick={subscribed ? this.onUnsubscribeClick : this.onSubscribeClick}
          disabled={!subscribed && (!consentChecked || !selectedAttributes.length)}
          loading={requesting}
        />

        <ConfirmDialog
          title="Confirm Unsubscribe"
          description="Unsubcribing will revoke all consents given and you will no longer have access to the benefits of this service"
          handleConfirm={() => this.onRequest(handleUnsubscribe)}
          open={confirmOpen}
          handleClose={() => this.setState({confirmOpen: false})}
        />
      </>
    );
  }

  async onSubscribeClick() {
    return this.onRequest(
      () => this.props.handleSubscribe(this.state.selectedAttributes, this.state.includeHistory));
  }

  getSensorAttributes() {
    const {apartment} = this.state;
    if (!apartment) return [];
    return _.flatten(apartment.apartment_sensors.map((sensor) => sensor.attributes.map((attr) => ({sensor, ...attr}))))
      .filter((attr) => this.props.service.requires.includes(attr.uri));
  }
}

export default ServiceSubscription;
