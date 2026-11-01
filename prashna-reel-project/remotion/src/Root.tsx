import React from 'react';
import {Composition} from 'remotion';
import {Reel} from './Reel';
import tl from './timeline.json';
export const Root: React.FC = () => (
  <Composition id="Reel" component={Reel} durationInFrames={Math.ceil((tl as any).total * 30)} fps={30} width={1080} height={1920} />
);
