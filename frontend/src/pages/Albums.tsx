// frontend/src/pages/Albums.tsx

import React from 'react';
import CreateAlbum from '../components/CentralNewsFeed/CreateAlbum';

const Albums: React.FC = () => {
  const handleAlbumCreated = () => {
    // Define what happens after an album is created
    console.log('Album created successfully!');
  };

  const sendAlbumMessage = () => {
    // Define how to send album messages
    console.log('Sending album message...');
  };

  return (
    <div>
      <h1>Albums Page</h1>
      <CreateAlbum onAlbumCreated={handleAlbumCreated} sendAlbumMessage={sendAlbumMessage} />
    </div>
  );
};

export default Albums;
