/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2012, 2018 University of Washington
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"

using namespace ns3;

// Run as 'NS_LOG="MM1Queue" ./waf --run mm1-queue' for logging output
NS_LOG_COMPONENT_DEFINE ("MM1Queue");

class Enqueuer : public Object
{
public:
  void SetQueue (Ptr<Queue<Packet> > queue) { m_queue = queue; }
  void SetNumPackets (uint32_t numPackets) { m_maxPackets = numPackets; }
  void SetGenerator (Ptr<ExponentialRandomVariable> var) { m_var = var; }
  bool IsRunning (void) { return m_running;}
  void Start (void);
  
private:
  void Generate (void);
  Ptr<Queue<Packet> > m_queue;
  Ptr<ExponentialRandomVariable> m_var;
  uint32_t m_maxPackets {0};
  uint32_t m_numPackets {0};
  bool m_running {false};
};

void
Enqueuer::Start (void)
{ 
  NS_LOG_FUNCTION (this);
  if (m_maxPackets > 0)
    {
      m_running = true;
      Simulator::Schedule (Seconds (m_var->GetValue ()), &Enqueuer::Generate, this);
    }
}
 
void
Enqueuer::Generate (void)
{
  if (m_numPackets < m_maxPackets)
    {
      NS_LOG_DEBUG ("Generating a packet at time " << Simulator::Now ().GetSeconds ());
      Ptr<Packet> p = Create<Packet> ();
      m_queue->Enqueue (p);
      Simulator::Schedule (Seconds (m_var->GetValue ()), &Enqueuer::Generate, this);
      m_numPackets++;
    }
  else
    {
      m_running = false;
    }
}

class Dequeuer : public Object
{
public:
  void SetQueue (Ptr<Queue<Packet> > queue) { m_queue = queue; }
  void SetGenerator (Ptr<ExponentialRandomVariable> var) { m_var = var; }
  void SetEnqueuer (Ptr<Enqueuer> enqueuer) { m_enqueuer = enqueuer; }
  void Start (void);
private:
  void Consume (void);
  Ptr<Queue<Packet> > m_queue;
  Ptr<ExponentialRandomVariable> m_var;
  Ptr<Enqueuer> m_enqueuer;
};

void
Dequeuer::Start (void)
{
  NS_LOG_FUNCTION (this);
  Simulator::Schedule (Seconds (m_var->GetValue ()), &Dequeuer::Consume, this); }

void
Dequeuer::Consume (void)
{
  NS_LOG_DEBUG ("Trying to dequeue  " << Simulator::Now ().GetSeconds ());
  Ptr<Packet> p = m_queue->Dequeue ();
  if (p)
    {
      NS_LOG_DEBUG ("Dequeue successful");
      Simulator::Schedule (Seconds (m_var->GetValue ()), &Dequeuer::Consume, this);
    }
  else
    {
      NS_LOG_DEBUG ("Dequeue failed (queue empty)");
      if (m_enqueuer && m_enqueuer->IsRunning ())
        {
          // Only keep rescheduling events if the enqueuer will fill the queue
          Simulator::Schedule (Seconds (m_var->GetValue ()), &Dequeuer::Consume, this);
        }
      else
        {
          NS_LOG_DEBUG ("Simulation should stop due to event queue exhaustion");
        }
    }
}

class QueueTracer
{
public:
  void Initialize (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue);
  static void EnqueueTracer (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue, Ptr<const Packet> p);  
  static void DequeueTracer (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue, Ptr<const Packet> p);  
  static void DropTracer (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue, Ptr<const Packet> p);  
};

void
QueueTracer::Initialize (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue)
{
  bool ok = queue->TraceConnectWithoutContext ("Enqueue", MakeBoundCallback (&QueueTracer::EnqueueTracer, stream, queue));
  NS_ABORT_MSG_UNLESS (ok == true, "Could not hook Enqueue trace source");
  ok = queue->TraceConnectWithoutContext ("Dequeue", MakeBoundCallback (&QueueTracer::DequeueTracer, stream, queue));
  NS_ABORT_MSG_UNLESS (ok == true, "Could not hook Dequeue trace source");
  ok = queue->TraceConnectWithoutContext ("Drop", MakeBoundCallback (&QueueTracer::DropTracer, stream, queue));
  NS_ABORT_MSG_UNLESS (ok == true, "Could not hook Drop trace source");
}

void
QueueTracer::EnqueueTracer (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue, Ptr<const Packet> p)
{
  NS_LOG_DEBUG ("Trace enqueue at time " << Simulator::Now ().GetSeconds ());
  *stream->GetStream () << Simulator::Now ().GetSeconds () << " + " << queue->GetNPackets () << std::endl;
}

void
QueueTracer::DequeueTracer (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue, Ptr<const Packet> p)
{
  NS_LOG_DEBUG ("Trace dequeue at time " << Simulator::Now ().GetSeconds ());
  *stream->GetStream () << Simulator::Now ().GetSeconds () << " - " << queue->GetNPackets () << std::endl;
}

void
QueueTracer::DropTracer (Ptr<OutputStreamWrapper> stream, Ptr<Queue<Packet> > queue, Ptr<const Packet> p)
{
  NS_LOG_DEBUG ("Trace drop at time " << Simulator::Now ().GetSeconds ());
  *stream->GetStream () << Simulator::Now ().GetSeconds () << " d " << queue->GetNPackets () << std::endl;
}


int main (int argc, char *argv[])
{
  bool quiet = false;
  uint32_t numInitialPackets = 0;
  uint32_t numPackets = 0;
  uint32_t queueLimit = 100; // packets
  double lambda = 1;
  double mu = 2;

  CommandLine cmd;
  cmd.AddValue ("lambda", "arrival rate (packets/sec)", lambda);
  cmd.AddValue ("mu", "departure rate (packets/sec)", mu);
  cmd.AddValue ("initialPackets", "initial packets in the queue", numInitialPackets);
  cmd.AddValue ("numPackets", "number of packets to enqueue", numPackets);
  cmd.AddValue ("queueLimit", "size of queue (number of packets)", queueLimit);
  cmd.AddValue ("quiet", "whether to suppress all output", quiet);
  cmd.Parse (argc, argv);

  NS_ABORT_MSG_UNLESS (lambda > 0, "Lambda must be > 0");
  NS_ABORT_MSG_UNLESS (mu > 0, "Mu must be > 0");
  NS_ABORT_MSG_UNLESS (lambda < mu, "Stability only if lamdba < mu");

  Ptr<DropTailQueue<Packet> > queue = CreateObject<DropTailQueue<Packet> > ();
  queue->SetMaxSize (QueueSize (QueueSizeUnit::PACKETS, queueLimit));
 
  Ptr<Enqueuer> enq = CreateObject<Enqueuer> ();
  enq->SetQueue (queue);
  enq->SetNumPackets (numPackets);
  Ptr<ExponentialRandomVariable> enqueueVar = CreateObject<ExponentialRandomVariable> ();
  enqueueVar->SetStream (1);
  enqueueVar->SetAttribute ("Mean", DoubleValue (1/lambda));
  enq->SetGenerator (enqueueVar);
  enq->Start ();

  Ptr<Dequeuer> deq = CreateObject<Dequeuer> ();
  deq->SetQueue (queue);
  deq->SetEnqueuer (enq);
  Ptr<ExponentialRandomVariable> dequeueVar = CreateObject<ExponentialRandomVariable> ();
  dequeueVar->SetStream (2);
  dequeueVar->SetAttribute ("Mean", DoubleValue (1/mu));
  deq->SetGenerator (dequeueVar);
  deq->Start ();

  // Trace events to an output file
  QueueTracer qt;
  AsciiTraceHelper asciiTraceHelper;
  Ptr<OutputStreamWrapper> stream = asciiTraceHelper.CreateFileStream ("mm1queue.dat");
  qt.Initialize (stream, queue);

  // Seed the queue with initial packets
  for (uint32_t i = 0; i < numInitialPackets; i++)
    {
      Ptr<Packet> p = Create<Packet> ();
      queue->Enqueue (p);
    }

  Simulator::Run ();
  Simulator::Destroy ();

  return 0;
}
