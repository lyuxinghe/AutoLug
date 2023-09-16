import React, { Component } from 'react';
import {
    Dimensions,
    View,
    TouchableWithoutFeedback,
    PanResponder
} from 'react-native';
import PropTypes from 'prop-types';
 
import {
    Connector,
    CONNECTOR_TOP_LEFT,
    CONNECTOR_TOP_MIDDLE,
    CONNECTOR_TOP_RIGHT,
    CONNECTOR_MIDDLE_RIGHT,
    CONNECTOR_BOTTOM_RIGHT,
    CONNECTOR_BOTTOM_MIDDLE,
    CONNECTOR_BOTTOM_LEFT,
    CONNECTOR_MIDDLE_LEFT,
    CONNECTOR_CENTER
} from './Connector';
 
import { Box } from './Box';
 
export const AXIS_X = 'x';
export const AXIS_Y = 'y';
export const AXIS_ALL = 'all';
 
const CONNECTOR_SIZE = 12;
const DEFAULT_Z_INDEX = 1;
 
/**
 * Drag resize block.
 */
export class BoundingBox extends Component {
 
    constructor(props) {
        super(props);
 
        const {
            initX,
            initY,
            initW,
            initH,
            minW,
            minH,
        } = props;
 
        let realX = (initX + initW) > this.props.limitation.w ? (this.props.limitation.w - initW - 2) : initX;
        let realY = (initY + initH) > this.props.limitation.h ? (this.props.limitation.h - initH - 2) : initY;
 
        this.state = {
            id: props.id,
            isSelected: false,
            x: realX,
            y: realY,
            w: initW < minW ? minW : initW,
            h: initH < minH ? minH : initH,
        };
 
        this.boxPosition = {
            x: 0,
            y: 0,
        };
 
        if (props.onCreate) {
            props.onCreate({id : props.id, x : this.state.x, y : this.state.y , w : this.state.w, h : this.state.h});
        }
        
        this._boxPanResponder = PanResponder.create({
            // Ask to be the responder:
            onStartShouldSetPanResponder: (event, gestureState) => true,
            onStartShouldSetPanResponderCapture: (event, gestureState) => true,
            onMoveShouldSetPanResponder: (event, gestureState) => true,
            onMoveShouldSetPanResponderCapture: (event, gestureState) => true,
 
            onPanResponderGrant: (event, gestureState) => {
 
                this.boxPosition = {
                    x: 0,
                    y: 0,
                };
 
                this.onDragStart([
                    0,
                    0,
                ]);
            },
            onPanResponderMove: (event, gestureState) => {
                this.onDrag([
                    gestureState.dx - this.boxPosition.x,
                    gestureState.dy - this.boxPosition.y,
                ]);
 
                this.boxPosition = {
                    x: gestureState.dx,
                    y: gestureState.dy,
                };
            },
            onPanResponderTerminationRequest: (event, gestureState) => true,
            onPanResponderRelease: (event, gestureState) => {
                this.onDragEnd([
                    gestureState.moveX,
                    gestureState.moveY,
                ]);
            },
            onPanResponderTerminate: (event, gestureState) => {
            },
            onShouldBlockNativeResponder: (event, gestureState) => {
                return true;
            },
        });
 
        /**
         * Connectors binding.
         */
        this.connectorsMap = {};
 
        /**
         * Top left connector.
         */
        this.connectorsMap[CONNECTOR_TOP_LEFT] = {
            calculateX: (width) => {
                return 0;
            },
            calculateY: (height) => {
                return 0;
            },
            onStart: this.onResizeStart,
            onMove: this.onResizeTL,
            onEnd: this.onResizeEnd,
        };
 
        if (typeof props.showTopMiddleConnector != 'undefined' && props.showTopMiddleConnector === true) {
            this.connectorsMap[CONNECTOR_TOP_MIDDLE] = {
                calculateX: (width) => {
                    return width / 2 - CONNECTOR_SIZE / 2;
                },
                calculateY: (height) => {
                    return 0;
                },
                onStart: this.onResizeStart,
                onMove: this.onResizeTM,
                onEnd: this.onResizeEnd,
            };
        }
 
        /**
         * Top right connector.
         */
        this.connectorsMap[CONNECTOR_TOP_RIGHT] = {
            calculateX: (width) => {
                return width - CONNECTOR_SIZE;
            },
            calculateY: (height) => {
                return 0;
            },
            onStart: this.onResizeStart,
            onMove: this.onResizeTR,
            onEnd: this.onResizeEnd,
            removable: (typeof props.removable != 'undefined') ? props.removable : true // check if the property removable is defined
        };
 
        if (typeof props.showMiddleRightConnector != 'undefined' && props.showMiddleRightConnector === true) {
            /**
             * Middle right connector.
             */
            this.connectorsMap[CONNECTOR_MIDDLE_RIGHT] = {
                calculateX: (width) => {
                    return width - CONNECTOR_SIZE;
                },
                calculateY: (height) => {
                    return height / 2 - CONNECTOR_SIZE / 2;
                },
                onStart: this.onResizeStart,
                onMove: this.onResizeMR,
                onEnd: this.onResizeEnd,
            };
        }
 
        /**
         * Bottom right connector.
         */
        this.connectorsMap[CONNECTOR_BOTTOM_RIGHT] = {
            calculateX: (width) => {
                return width - CONNECTOR_SIZE;
            },
            calculateY: (height) => {
                return height - CONNECTOR_SIZE;
            },
            onStart: this.onResizeStart,
            onMove: this.onResizeBR,
            onEnd: this.onResizeEnd,
        };
 
        /**
         * Bottom middle connector.
         */
        if (typeof props.showBottomMiddleConnector != 'undefined' && props.showBottomMiddleConnector === true) {
            this.connectorsMap[CONNECTOR_BOTTOM_MIDDLE] = {
                calculateX: (width) => {
                    return width / 2 - CONNECTOR_SIZE / 2;
                },
                calculateY: (height) => {
                    return height - CONNECTOR_SIZE;
                },
                onStart: this.onResizeStart,
                onMove: this.onResizeBM,
                onEnd: this.onResizeEnd,
            };
        }
 
 
        /**
         * Bottom left connector.
         */
        this.connectorsMap[CONNECTOR_BOTTOM_LEFT] = {
            calculateX: (width) => {
                return 0;
            },
            calculateY: (height) => {
                return height - CONNECTOR_SIZE;
            },
            onStart: this.onResizeStart,
            onMove: this.onResizeBL,
            onEnd: this.onResizeEnd,
        };
 
        if (typeof props.showMiddleLeftConnector != 'undefined' && props.showMiddleLeftConnector === true) {
            /**
             * Middle left connector.
             */
            this.connectorsMap[CONNECTOR_MIDDLE_LEFT] = {
                calculateX: (width) => {
                    return 0;
                },
                calculateY: (height) => {
                    return height / 2 - CONNECTOR_SIZE / 2;
                },
                onStart: this.onResizeStart,
                onMove: this.onResizeML,
                onEnd: this.onResizeEnd,
            };
        }
 
        if (typeof props.showCenterConnector != 'undefined' && props.showCenterConnector === true) {
            /**
             * Center connector.
             */
            this.connectorsMap[CONNECTOR_CENTER] = {
                calculateX: (width) => {
                    return width / 2 - CONNECTOR_SIZE / 2;
                },
                calculateY: (height) => {
                    return height / 2 - CONNECTOR_SIZE / 2;
                },
                onStart: this.onDragStart,
                onMove: this.onDrag,
                onEnd: this.onDragEnd,
            };
        }
    }
 
    /**
     * Handle press event.
     * @param {Event} event - Press event.
     */
    onPress = (event) => {
        const {
            onPress,
        } = this.props;
 
        if (onPress !== null) {
            onPress(event);
        }
    }
 
    /**
     * Handle resize start event.
     * @param {Array} coord - Press coordinate [x,y].
     */
    onResizeStart = (coord) => {
        const {
            onResizeStart,
        } = this.props;
 
        this.setState(() => {
            return {
                isSelected: true,
            };
        });
 
        if (onResizeStart !== null) {
            onResizeStart({
                x: this.state.x,
                y: this.state.y,
                w: this.state.w,
                h: this.state.h
            });
        }
    }
 
    onResizeTL = (coord) => {
        const {
            minW,
            minH,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newX = this.state.x + coord[0];
            const newY = this.state.y + coord[1];
            const newW = this.state.x + this.state.w - newX;
            const newH = this.state.y + this.state.h - newY;
 
            if (newW >= minW && axis != AXIS_Y) {
                if (limitation.x <= newX) {
                    this.state.w = newW;
                    this.state.x = newX;
                }
            }
 
            if (newH >= minH && axis != AXIS_X) {
                if (limitation.y <= newY) {
                    this.state.h = newH;
                    this.state.y = newY;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    onResizeTM = (coord) => {
        const {
            minH,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newY = this.state.y + coord[1];
            const newH = this.state.y + this.state.h - newY;
 
            if (newH >= minH && axis != AXIS_X) {
                if (limitation.y <= newY) {
                    this.state.h = newH;
                    this.state.y = newY;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    onResizeTR = (coord) => {
        const {
            minW,
            minH,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newY = this.state.y + coord[1];
            const newW = this.state.w + coord[0];
            const newH = this.state.y + this.state.h - newY;
 
            if (newW >= minW && axis != AXIS_Y) {
                if (limitation.w >= this.state.x + newW) {
                    this.state.w = newW;
                }
            }
 
            if (newH >= minH && axis != AXIS_X) {
                if (limitation.y <= newY) {
                    this.state.h = newH;
                    this.state.y = newY;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    onResizeMR = (coord) => {
        const {
            minW,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newW = this.state.w + coord[0];
 
            if (newW >= minW && axis != AXIS_Y) {
                if (limitation.w >= this.state.x + newW) {
                    this.state.w = newW;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    onResizeBR = (coord) => {
        const {
            minW,
            minH,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newW = this.state.w + coord[0];
            const newH = this.state.h + coord[1];
 
            if (newW >= minW && axis != AXIS_Y) {
                if (limitation.w >= this.state.x + newW) {
                    this.state.w = newW;
                }
            }
 
            if (newH >= minH && axis != AXIS_X) {
                if (limitation.h >= this.state.y + newH) {
                    this.state.h = newH;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    onResizeBM = (coord) => {
        const {
            minH,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newH = this.state.h + coord[1];
 
            if (newH >= minH && axis != AXIS_X) {
                if (limitation.h >= this.state.y + newH) {
                    this.state.h = newH;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    onResizeBL = (coord) => {
        const {
            minW,
            minH,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newX = this.state.x + coord[0];
            const newW = this.state.x + this.state.w - newX;
            const newH = this.state.h + coord[1];
 
            if (newW >= minW && axis != AXIS_Y) {
                if (limitation.x <= newX) {
                    this.state.w = newW;
                    this.state.x = newX;
                }
            }
 
            if (newH >= minH && axis != AXIS_X) {
                if (this.state.y + newH <= limitation.h) {
                    this.state.h = newH;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    onResizeML = (coord) => {
        const {
            minW,
            axis,
            isResizable,
            limitation,
            onResize,
        } = this.props;
 
        if (!isResizable) {
            return;
        }
 
        this.setState(() => {
            const newX = this.state.x + coord[0];
            const newW = this.state.x + this.state.w - newX;
 
            if (newW >= minW && axis != AXIS_Y) {
                if (limitation.x <= newX) {
                    this.state.w = newW;
                    this.state.x = newX;
                }
            }
 
            if (onResize !== null) {
                onResize({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    /**
     * Handle resize end event.
     * @param {Array} coord - Press coordinate [x,y].
     */
    onResizeEnd = (coord) => {
        const {
            onResizeEnd,
        } = this.props;
 
        this.setState(() => {
            return {
                isSelected: false,
            };
        });
 
        if (onResizeEnd !== null) {
            onResizeEnd({
                x: this.state.x,
                y: this.state.y,
                w: this.state.w,
                h: this.state.h
            });
        }
    }
 
    /**
     * Handle drag start event.
     * @param {Array} coord - Press coordinate [x,y].
     */
    onDragStart = (coord) => {
        const {
            onDragStart,
        } = this.props;
 
        this.setState(() => {
            return {
                isSelected: true,
            };
        });
 
        if (onDragStart !== null) {
            onDragStart({
                x: this.state.x,
                y: this.state.y,
                w: this.state.w,
                h: this.state.h
            });
        }
    }
 
    _onRemove = () => {
        const {
            onRemove,
        } = this.props;
 
        onRemove(this);
    }
 
    /**
     * Handle drag event.
     * @param {Array} coord - Press coordinate [x,y].
     */
    onDrag = (coord) => {
        const {
            axis,
            isDraggable,
            limitation,
            onDrag,
        } = this.props;
 
        if (!isDraggable) {
            return;
        }
 
        this.setState(() => {
            const newX = this.state.x + coord[0];
            const newY = this.state.y + coord[1];
 
            if (axis != AXIS_Y) {
                if (limitation.x <= newX && limitation.w >= newX + this.state.w) {
                    this.state.x = newX;
                }
            }
 
            if (axis != AXIS_X) {
                if (limitation.y <= newY && limitation.h >= newY + this.state.h) {
                    this.state.y = newY;
                }
            }
 
            if (onDrag !== null) {
                onDrag({
                    x: this.state.x,
                    y: this.state.y,
                    w: this.state.w,
                    h: this.state.h
                });
            }
 
            return this.state;
        });
    }
 
    /**
     * Handle drag end event.
     * @param {Array} coord - Press coordinate [x,y].
     */
    onDragEnd = (coord) => {
        const {
            onDragEnd,
        } = this.props;
 
        this.setState(() => {
            return {
                isSelected: false,
            };
        });
 
        if (onDragEnd !== null) {
            onDragEnd({
                x: this.state.x,
                y: this.state.y,
                w: this.state.w,
                h: this.state.h
            });
        }
    }
 
    /**
     * Render connector components.
     */
    renderConnectors = () => {
        const {
            connectors,
        } = this.props;
 
        const {
            w,
            h,
        } = this.state;
 
        return connectors.filter((c) => {
            if (c == CONNECTOR_TOP_MIDDLE) {
                if (typeof this.props.showTopMiddleConnector != 'undefined' && this.props.showTopMiddleConnector === true) {
                    return c;
                }
            } else if (c == CONNECTOR_BOTTOM_MIDDLE) {
                if (typeof this.props.showBottomMiddleConnector != 'undefined' && this.props.showBottomMiddleConnector === true) {
                    return c;
                }
            } else if (c == CONNECTOR_MIDDLE_LEFT) {
                if (typeof this.props.showMiddleLeftConnector != 'undefined' && this.props.showMiddleLeftConnector === true) {
                    return c;
                }
            } else if (c == CONNECTOR_MIDDLE_RIGHT) {
                if (typeof this.props.showMiddleRightConnector != 'undefined' && this.props.showMiddleRightConnector === true) {
                    return c;
                }
            } else if (c == CONNECTOR_CENTER) {
                if (typeof this.props.showCenterConnector != 'undefined' && this.props.showCenterConnector === true) {
                    return c;
                }
            } else {
                return c;
            }
        }).map((connectorType) => {
            return (
                <Connector
                    key={connectorType}
                    type={connectorType}
                    size={this.props.connectorWidth ? props.connectorWidth : CONNECTOR_SIZE}
                    x={this.connectorsMap[connectorType].calculateX(w)}
                    y={this.connectorsMap[connectorType].calculateY(h)}
                    onStart={this.connectorsMap[connectorType].onStart}
                    onMove={this.connectorsMap[connectorType].onMove}
                    onEnd={this.connectorsMap[connectorType].onEnd}
                    removable={this.connectorsMap[connectorType].removable}
                    onRemove={this._onRemove}
                />
            );
        });
    }
 
    render() {
        const {
            isDisabled,
            zIndex,
            connectorWidth
        } = this.props;
 
        const {
            x,
            y,
            w,
            h,
            isSelected,
        } = this.state;
 
        return (
            <View
                style={{
                    position: 'absolute',
                    left: x,
                    top: y,
                    width: w,
                    height: h,
                    padding: connectorWidth ? (connectorWidth / 2) : (CONNECTOR_SIZE / 2),
                    zIndex: isSelected ? zIndex + 1 : zIndex,
                }}
            >
                <TouchableWithoutFeedback
                    onPress={this.onPress}
                >
                    <View
                        style={{
                            width: '100%',
                            height: '100%',
                        }}
                    >
                        <Box
                            borderColor={this.props.boxBoderColor}
                            boxBackground={this.props.boxBackground}
                            onStart={this.onDragStart}
                            onMove={this.onDrag}
                            onEnd={this.onDragEnd}
                        />
                    </View>
                </TouchableWithoutFeedback>
 
                {isDisabled ? null : this.renderConnectors()}
 
            </View>
        );
    }
}
 
BoundingBox.defaultProps = {
    x: 0,
    y: 0,
    w: 100,
    h: 100,
    minW: 50,
    minH: 50,
    axis: AXIS_ALL,
    limitation: {
        x: 0,
        y: 0,
        w: Dimensions.get('window').width,
        h: Dimensions.get('window').height,
    },
    isDisabled: false,
    zIndex: DEFAULT_Z_INDEX,
    isDraggable: true,
    isResizable: true,
    connectors: [
        CONNECTOR_TOP_LEFT,
        CONNECTOR_TOP_MIDDLE,
        CONNECTOR_TOP_RIGHT,
        CONNECTOR_MIDDLE_RIGHT,
        CONNECTOR_BOTTOM_RIGHT,
        CONNECTOR_BOTTOM_MIDDLE,
        CONNECTOR_BOTTOM_LEFT,
        CONNECTOR_MIDDLE_LEFT,
        CONNECTOR_CENTER,
    ],
 
    onPress: null,
    onDragStart: null,
    onDrag: null,
    onDragEnd: null,
    onResizeStart: null,
    onResize: null,
    onResizeEnd: null,
};
 
BoundingBox.propTypes = {
    id: PropTypes.string,
    initX: PropTypes.number,
    initY: PropTypes.number,
    initW: PropTypes.number,
    initH: PropTypes.number,
    minW: PropTypes.number,
    minH: PropTypes.number,
    zIndex: PropTypes.number,
    axis: PropTypes.oneOf([
        AXIS_X,
        AXIS_Y,
        AXIS_ALL,
    ]),
    limitation: PropTypes.shape({
        x: PropTypes.number.isRequired,
        y: PropTypes.number.isRequired,
        w: PropTypes.number.isRequired,
        h: PropTypes.number.isRequired,
    }),
    isDisabled: PropTypes.bool,
    isDraggable: PropTypes.bool,
    isResizable: PropTypes.bool,
    connectors: PropTypes.array,
    onPress: PropTypes.func,
    onDragStart: PropTypes.func,
    onCreate: PropTypes.func,
    onDrag: PropTypes.func,
    onDragEnd: PropTypes.func,
    onResizeStart: PropTypes.func,
    onResize: PropTypes.func,
    onResizeEnd: PropTypes.func,
    showTopMiddleConnector: PropTypes.bool,// true to show connector 
    showMiddleRightConnector: PropTypes.bool,// true to show connector 
    showBottomMiddleConnector: PropTypes.bool,// true to show connector 
    showMiddleLeftConnector: PropTypes.bool,// true to show connector 
    showCenterConnector: PropTypes.bool, // true to show connector 
    removable: PropTypes.bool, // true to show blue remove button at the right top corner
    connectorWidth: PropTypes.number, // the connector width
    boxBoderColor: PropTypes.string, // the box's border color
    boxBackground: PropTypes.string, // the box's background color
    onRemove: PropTypes.func  // when click the remove button
};