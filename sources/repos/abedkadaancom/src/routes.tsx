import { lazy, Suspense, type ReactNode } from 'react';
import type { RouteObject } from 'react-router-dom';
import { Layout } from './ui/Layout';
import { Home } from './pages/Home';
import { Gate } from './pages/Gate';
import { Atrium, DivisionPage, TopicPage } from './pages/Divisions';
import { Library, CgtReader, SpecimenPage } from './pages/Library';
import { HarnessMasters } from './pages/HarnessMasters';
import { HarnessHome, HarnessStation } from './pages/Harness';
import { Scriptorium, BookReader } from './pages/Scriptorium';
import { CommonRoom } from './pages/CommonRoom';
import { Glossary, GlossaryTerm } from './pages/Glossary';
import { About } from './pages/About';
import { NotFound } from './pages/NotFound';

const ObservatoryPage = lazy(() => import('./pages/Observatory').then((m) => ({ default: m.Observatory })));
const wait = (el: ReactNode) => <Suspense fallback={<p className="muted">Opening the dome…</p>}>{el}</Suspense>;

/** The public route table. Every campus space has a direct address that loads its scene without the intro. */
export const ROUTE_PATHS = [
  '/',
  '/gate',
  '/atrium',
  '/divisions/:id',
  '/divisions/:id/:topic',
  '/library',
  '/library/computational-grammar-theory',
  '/library/specimens/:id',
  '/observatory',
  '/observatory/sky',
  '/harness-masters',
  '/harness',
  '/harness/:division',
  '/scriptorium',
  '/scriptorium/:bookId',
  '/common-room',
  '/glossary',
  '/glossary/:term',
  '/about',
] as const;

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'gate', element: <Gate /> },
      { path: 'atrium', element: <Atrium /> },
      { path: 'divisions/:id', element: <DivisionPage /> },
      { path: 'divisions/:id/:topic', element: <TopicPage /> },
      { path: 'library', element: <Library /> },
      { path: 'library/computational-grammar-theory', element: <CgtReader /> },
      { path: 'library/specimens/:id', element: <SpecimenPage /> },
      { path: 'observatory', element: wait(<ObservatoryPage />) },
      { path: 'observatory/sky', element: wait(<ObservatoryPage />) },
      { path: 'harness-masters', element: <HarnessMasters /> },
      { path: 'harness', element: <HarnessHome /> },
      { path: 'harness/:division', element: <HarnessStation /> },
      { path: 'scriptorium', element: <Scriptorium /> },
      { path: 'scriptorium/:bookId', element: <BookReader /> },
      { path: 'common-room', element: <CommonRoom /> },
      { path: 'glossary', element: <Glossary /> },
      { path: 'glossary/:term', element: <GlossaryTerm /> },
      { path: 'about', element: <About /> },
      { path: '*', element: <NotFound /> },
    ],
  },
];
