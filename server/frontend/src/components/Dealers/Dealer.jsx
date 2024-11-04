import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import "./Dealers.css";
import "../assets/style.css";
import positive_icon from "../assets/positive.png";
import neutral_icon from "../assets/neutral.png";
import negative_icon from "../assets/negative.png";
import review_icon from "../assets/reviewbutton.png";
import Header from '../Header/Header';

const Dealer = () => {
  const [dealer, setDealer] = useState(null); // Set to null initially
  const [reviews, setReviews] = useState([]);
  const [unreviewed, setUnreviewed] = useState(false);
  const [postReview, setPostReview] = useState(<></>);

  const { id } = useParams();
  const curr_url = window.location.href;
  const root_url = curr_url.substring(0, curr_url.indexOf("dealer"));
  const dealer_url = `${root_url}djangoapp/dealer/${id}`;
  const reviews_url = `${root_url}djangoapp/reviews/dealer/${id}`;
  const post_review = `${root_url}postreview/${id}`;

  const get_dealer = async () => {
    try {
      const res = await fetch(dealer_url, { method: "GET" });
      const retobj = await res.json();
      if (retobj.status === 200) {
        setDealer(retobj.dealer || null);
      }
    } catch (error) {
      console.error("Failed to fetch dealer:", error);
    }
  };

  const get_reviews = async () => {
    try {
      const res = await fetch(reviews_url, { method: "GET" });
      const retobj = await res.json();

      if (retobj.status === 200) {
        if (retobj.reviews.length > 0) {
          setReviews(retobj.reviews);
        } else {
          setUnreviewed(true);
        }
      }
    } catch (error) {
      console.error("Failed to fetch reviews:", error);
    }
  };

  const senti_icon = (sentiment) => {
    return sentiment === "positive" ? positive_icon : sentiment === "negative" ? negative_icon : neutral_icon;
  };

  useEffect(() => {
    get_dealer();
    get_reviews();
    if (sessionStorage.getItem("username")) {
      setPostReview(
        <a href={post_review}>
          <img src={review_icon} className="review_icon" style={{ width: '100px', marginLeft: '10px' }} alt='Post Review' />
        </a>
      );
    }
  }, []);

  return (
    <div>
      <Header />
      <div className="text-center">
        {dealer ? (
          <>
            <h1 className="text-primary">{dealer.full_name} {postReview}</h1>
            <h5 className="text-muted">
              {dealer.city}, {dealer.address}, Zip - {dealer.zip}, {dealer.state}
            </h5>
          </>
        ) : (
          <div className="spinner-border text-primary" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        )}
      </div>

      <div className="reviews_panel mt-5">
        {reviews.length === 0 && unreviewed === false ? (
          <div className="text-center">Loading Reviews...</div>
        ) : unreviewed === true ? (
          <div className="alert alert-info text-center">No reviews yet!</div>
        ) : (
          <div className="row">
            {reviews.map((review, index) => (
              <div className="col-md-6 col-lg-4 mb-4" key={index}>
                <div className="card shadow-sm">
                  <div className="card-body">
                    <img src={senti_icon(review.sentiment)} className="emotion_icon img-fluid mb-3" alt="Sentiment" />
                    <p className="card-text">{review.review}</p>
                    <p className="card-text text-muted small">
                      {review.name} - {review.car_make} {review.car_model} ({review.car_year})
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dealer;
