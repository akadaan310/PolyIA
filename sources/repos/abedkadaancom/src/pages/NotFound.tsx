import { Link } from 'react-router-dom';
import { usePageTitle } from '../ui/bits';

export function NotFound() {
  usePageTitle('No such place');
  return (
    <article>
      <h1>No such place on campus</h1>
      <p>This path does not lead anywhere. In grammar terms: syntactically admissible, but not realizable.</p>
      <p>
        <Link to="/">Return to the Approach</Link> · <Link to="/atrium">Go to the Atrium</Link> · <Link to="/library/computational-grammar-theory">Looking for the Computational Grammar Theory book?</Link>
      </p>
    </article>
  );
}
