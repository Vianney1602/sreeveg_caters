import React, { useState } from 'react';
import './BulkOrderModal.css';

function BulkOrderModal({ isOpen, onClose, onSubmit, eventType }) {
  const [formData, setFormData] = useState({
    numberOfPersons: '',
    eventDate: '',
    eventLocation: '',
    eventTiming: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.numberOfPersons && formData.eventDate && formData.eventLocation && formData.eventTiming) {
      onSubmit(formData);
    } else {
      alert('Please fill in all fields');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Bulk Order Details - {eventType}</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="numberOfPersons">Number of Persons *</label>
            <input
              type="number"
              id="numberOfPersons"
              name="numberOfPersons"
              value={formData.numberOfPersons}
              onChange={handleChange}
              min="10"
              placeholder="Enter number of guests"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="eventDate">Event Date *</label>
            <input
              type="date"
              id="eventDate"
              name="eventDate"
              value={formData.eventDate}
              onChange={handleChange}
              min={new Date().toISOString().split('T')[0]}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="eventLocation">Event Location *</label>
            <input
              type="text"
              id="eventLocation"
              name="eventLocation"
              value={formData.eventLocation}
              onChange={handleChange}
              placeholder="Enter event location"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="eventTiming">Event Timing *</label>
            <input
              type="time"
              id="eventTiming"
              name="eventTiming"
              value={formData.eventTiming}
              onChange={handleChange}
              required
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="submit-btn">Proceed to Menu</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default BulkOrderModal;
