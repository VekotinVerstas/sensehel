import React from 'react';
import FormControlLabel from '@material-ui/core/FormControlLabel/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox/Checkbox';
import { green, grey } from '@material-ui/core/colors';
import { withStyles } from '@material-ui/core';

const styles = {
  root: {
    '&$checked': {
      color: green[500]
    }
  },
  checked: {
    color: green[500]
  },
  disabled: {
    '&$checked': {
      color: grey[500]
    }
  }
};

const CheckboxesSection = ({
  consentChecked,
  handleChange,
  disabled,
  termsAndConditions,
  classes
}) => (
  <div className="card-section">
    <FormControlLabel
      control={
        <Checkbox
          checked={consentChecked}
          onChange={() => handleChange('consentChecked')}
          classes={{
            root: classes.root,
            checked: classes.checked,
            disabled: classes.disabled
          }}
          disabled={disabled}
        />
      }
      label={
        <span className="body-text">
          I have read and understood
          the <a href={termsAndConditions} target="_blank" rel="noopener noreferrer" className="body-text">
            <b>terms and conditions</b>
          </a> and consent to my details being stored *
        </span>
      }
    />
  </div>
);

export default withStyles(styles)(CheckboxesSection);
