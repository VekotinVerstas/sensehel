import React, { Component } from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';
import Slide from '@material-ui/core/Slide/Slide';
import Collapse from '@material-ui/core/Collapse/Collapse';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';
import Fade from '@material-ui/core/Fade/Fade';
import Images from '../../assets/Images';

import './card.styles.css';

const styles = theme => ({
  expand: {
    float: 'right',
    margin: 5,
    transform: 'rotate(0deg)',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest
    })
  },
  expandOpen: {
    transform: 'rotate(180deg)'
  }
});

class Card extends Component {
  state = {
    expanded: false
  };

  handleExpandClick = () => {
    const { expanded } = this.state;
    this.setState({ expanded: !expanded });
  };

  render() {
    const {
      image,
      name,
      description,
      CollapsibleComponent,
      classes
    } = this.props;
    const { expanded } = this.state;

    return (
      <div className="card">
        <div className="card__row">
          <div className="card__col1">
            <img src={image} className="service-logo" alt="service" />
          </div>

          <div className="card__col2">
            <p className="headline card__text">{name}</p>
            <p className="body-text card__text">{description}</p>
          </div>

          <div className="card__col3">
            <IconButton
              className={classNames(classes.expand, {
                [classes.expandOpen]: expanded
              })}
              onClick={this.handleExpandClick}
              aria-expanded={expanded}
              aria-label="Show more"
            >
              <ExpandMoreIcon />
            </IconButton>
          </div>
        </div>

        <Collapse in={expanded} timeout="auto" mountOnEnter unmountOnExit>
          <Slide
            direction="down"
            in={expanded}
            timeout={500}
            mountOnEnter
            unmountOnExit
          >
            {CollapsibleComponent}
          </Slide>
        </Collapse>
      </div>
    );
  }
}

Card.propTypes = {
  image: PropTypes.any, // eslint-disable-line
  name: PropTypes.string.isRequired,
  description: PropTypes.string,
  CollapsibleComponent: PropTypes.node
};

Card.defaultProps = {
  image: Images.Placeholder,
  description: '',
  CollapsibleComponent: null
};

export default withStyles(styles)(Card);
