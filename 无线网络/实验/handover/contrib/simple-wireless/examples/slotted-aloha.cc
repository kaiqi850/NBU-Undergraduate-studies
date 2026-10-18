/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright 2018 University of Washington
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

// This is a program to evaluate slotted aloha with ns3::SimpleWireless
//
// Network topology:  n nodes scattered at a dropping radius of distance r
// around origin.  n0 is the receiver.  n1...(n-1) are sendingNodes contending
// for the channel.
//
//         , - ~ ~ ~ - ,
//     , '               ' ,
//   ,   n5(etc.)            ,
//  ,               n1        ,
// ,                           ,
// ,<--- r ---> n0             ,
// ,                    n4     ,
//  ,      n3                 ,
//   ,                       ,
//     ,      n2          , '
//       ' - , _ _ _ ,  '
//
// Credit:  Circle ascii art copied from http://ascii.co.uk/art/circle
//
// Users may vary the following command-line arguments in addition to the
// attributes, global values, and default values typically available:
//
// The default data rate of the link is 10 Mbps.  Each packet size is 125
// bytes (1000 bits), so it takes 100 microseconds to notionally transmit
// a packet.
//
// Each slot is 100 microseconds long.  Each sender can send at most 1 
// packet per slot.
//
// Packets arrive to the system according to a Poisson process with rate
// lambda, in units of slot times.  That is, a lambda of 1 corresponds to
// one new packet arriving on average to the system each slot (note:  this
// will overload the system).  Lambda defaults to 0.1 but can be changed
// as a command line argument.
//
// The simulation will run until 'maxPackets' are received.  If transmissions
// collide, the packets will be recirculated and a backoff scheduled.
// The backoff process is simple:  if a packet collides, then it is
// rescheduled for a slot uniformly in the range (0, number of nodes).
// Therefore, collisions will increase the intensity of arrivals to the
// system.
//

#include <fstream>
#include <iostream>
#include <iomanip>
#include <cmath>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/propagation-module.h"
#include "ns3/simple-wireless-channel.h"
#include "ns3/simple-wireless-net-device.h"
#include "ns3/snr-per-error-model.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("SlottedAlohaExample");

std::ofstream g_fileSummary;
uint64_t g_numPacketsSent = 0;
uint64_t g_numPacketsReceived = 0;
uint64_t g_numPacketsDropped = 0;
uint64_t g_maxPackets = 0;
uint64_t g_slotArrivals = 0;
uint64_t g_slotArrivalsSinceLastReport = 0;
uint64_t g_lastReceivedCount = 0;
uint64_t g_slotsWithoutProgress = 0;
uint64_t g_maxSlotsWithoutProgress = 0;

void
ReportProgress (Time reportingInterval)
{
  std::cout << "*** Simulation time: " << std::fixed << std::setprecision (3) << Simulator::Now ().GetSeconds () << "s; total received: " << g_numPacketsReceived << "; sent since last report: " << g_slotArrivalsSinceLastReport << std::endl;
  g_slotArrivalsSinceLastReport = 0;
  Simulator::Schedule (reportingInterval, &ReportProgress, reportingInterval);
}

void
TransmitTrace (Ptr<const Packet> p, Mac48Address from, Mac48Address to, uint16_t proto)
{
  g_numPacketsSent++;
}

void
MacReceiveTrace (Ptr<const Packet> p)
{
  g_numPacketsReceived++;
}

void
DropTrace (Ptr<const Packet> p, double rxPower, Mac48Address from)
{
  g_numPacketsDropped++;
}

void
ReceivePacket (Ptr<Socket> socket)
{
  Ptr<Packet> packet;
  while ((packet = socket->Recv ()))
    {
      NS_LOG_DEBUG ("Receiving " << packet->GetSize ());
    }
}

void
PoissonArrivalProcess (Ptr<ExponentialRandomVariable> ranVar)
{
  g_slotArrivals++;
  double nextTime = ranVar->GetValue ();
  // nextTime is in units of slots; i.e. 100 us, so scale by 1/10000
  nextTime /= 10000;
  Simulator::Schedule (Seconds (nextTime), &PoissonArrivalProcess, ranVar);
}

void
RetransmissionArrival (void)
{
  NS_LOG_DEBUG ("Retransmission arrival");
  g_slotArrivals++;
}

void
SlotArrivalProcess (Time slotTime, uint32_t nextSender, std::vector<Ptr<PacketSocketClient> > socketVector, Ptr<UniformRandomVariable> backoffVar)
{
  // For reporting progress, when verbose flag is set
  g_slotArrivalsSinceLastReport += g_slotArrivals;
  if (g_numPacketsReceived == g_lastReceivedCount)
    {
      g_slotsWithoutProgress++;
    }
  else
    {
      g_slotsWithoutProgress = 0;
      g_lastReceivedCount = g_numPacketsReceived;
    }
  if (g_numPacketsReceived >= g_maxPackets)
    {
      Simulator::Stop ();
      return;
    }
  if (g_slotsWithoutProgress >= g_maxSlotsWithoutProgress)
    {
      // The system has become unstable and not making progress
      Simulator::Stop ();
      return;
    }
  // Send one packet (on a different node) for each arrival that
  // occurred during the last slot.  Loop through the available sending
  // nodes sequentially
  uint32_t maxId = socketVector.size () - 1;
  for (uint32_t i = 0; i < g_slotArrivals; i++, nextSender++)
    {
      if (nextSender > maxId)
        {
          nextSender = 0;
        }
      Ptr<PacketSocketClient> client = socketVector[nextSender];
      NS_LOG_DEBUG ("Sending packet from sender " << nextSender);
      client->SendOnDemand ();
    }
  if (g_slotArrivals > 1)
    {
      // These packets will collide and need to be rescheduled some time
      // in the future.  Pick a random number of slots in the future,
      // corresponding to the size of the network, to retry.  They will
      // be sent out from another node, but it doesn't matter for the
      // analysis.
      for (uint32_t i = 0; i < g_slotArrivals; i++)
        {
          uint32_t backoffSlots = backoffVar->GetInteger ();
          NS_LOG_DEBUG ("Retransmission backoff for " << backoffSlots << " slots");
          Simulator::Schedule (MicroSeconds (100) * backoffSlots, &RetransmissionArrival);
        }
    }
  g_slotArrivals = 0;
  Simulator::Schedule (slotTime, &SlotArrivalProcess, slotTime, nextSender, socketVector, backoffVar); 
}

int
main (int argc, char *argv[])
{
  DataRate dataRate = DataRate ("10Mbps");
  double radius = 25; // m
  uint32_t packetSize = 125; // bytes
  uint32_t numSenders = 100;
  double noisePower = -100; // dbm
  double lambda = 0.1;
  Time slotTime = MicroSeconds (100);
  Time reportingInterval = MilliSeconds (1);
  bool verbose = false;

  g_numPacketsSent = 0;
  g_numPacketsReceived = 0;
  g_numPacketsDropped = 0;
  g_maxPackets = 1000;
  // Terminate the simulation if no progress is made for 100 slots
  g_maxSlotsWithoutProgress = 100;

  CommandLine cmd;
  cmd.AddValue ("lambda", "Arrival lambda (i.e. rate, or 1/mean); units of slots", lambda);
  cmd.AddValue("maxPackets", "the number of packets to send", g_maxPackets);
  cmd.AddValue("numSenders", "number of sendingNodes" , numSenders);
  cmd.AddValue("verbose", "verbose output", verbose);
  cmd.Parse (argc, argv);

  Ptr<ExponentialRandomVariable> ranVar = CreateObject<ExponentialRandomVariable> (); 
  ranVar->SetAttribute ("Mean", DoubleValue (1/lambda));

  Ptr<UniformRandomVariable> backoffVar = CreateObject<UniformRandomVariable> ();
  backoffVar->SetAttribute ("Max", DoubleValue (numSenders));

  Ptr<Node> receiverNode = CreateObject<Node> ();
  NodeContainer sendingNodes;
  sendingNodes.Create (numSenders);
  NodeContainer nodes;
  nodes.Add (receiverNode);
  nodes.Add (sendingNodes);

  // Set the receiver at the coordinate (0, 0, 0)
  Ptr<ConstantPositionMobilityModel> mobilityModel = CreateObject<ConstantPositionMobilityModel> ();
  mobilityModel->SetPosition (Vector (0, 0, 0));
  receiverNode->AggregateObject (mobilityModel);
  
  // Use a mobility helper to scatter the sender nodes around the receiver
  MobilityHelper mobility;
  Ptr<UniformDiscPositionAllocator> positionAllocator = CreateObject<UniformDiscPositionAllocator> ();
  positionAllocator->SetX (0);
  positionAllocator->SetY (0);
  positionAllocator->SetRho (radius);
  mobility.SetPositionAllocator (positionAllocator);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (sendingNodes);

  auto lossModel = CreateObject<FriisPropagationLossModel> ();
  lossModel->SetFrequency (5e9);  // 5 GHz

  Ptr<SimpleWirelessChannel> channel = CreateObject<SimpleWirelessChannel> ();
  channel->AddPropagationLossModel (lossModel);

  NetDeviceContainer devices;
  Mac48Address receiverAddress = Mac48Address::Allocate ();

  Ptr<SimpleWirelessNetDevice> receiverDevice = CreateObject<SimpleWirelessNetDevice> ();
  receiverDevice->SetChannel (channel);
  receiverDevice->SetNode (receiverNode);
  receiverDevice->SetAddress (receiverAddress);
  receiverDevice->SetDataRate (dataRate);
  receiverDevice->SetNoisePower (noisePower);
  receiverDevice->TraceConnectWithoutContext ("MacRx", MakeCallback (&MacReceiveTrace));
  receiverDevice->TraceConnectWithoutContext ("PhyRxDrop", MakeCallback (&DropTrace));
  Ptr<BpskSnrPerErrorModel> errorModel = CreateObject<BpskSnrPerErrorModel> ();
  receiverDevice->SetSnrPerErrorModel (errorModel);
  receiverDevice->SetAttribute ("SlottedAloha", BooleanValue (true));
  Ptr<DropTailQueue<Packet>> queue = CreateObject<DropTailQueue<Packet>> ();
  queue->SetMaxSize (QueueSize (QueueSizeUnit::PACKETS, 100));
  receiverDevice->SetQueue (queue);
  receiverNode->AddDevice (receiverDevice);
  devices.Add (receiverDevice);

  std::vector<Ptr<SimpleWirelessNetDevice> > senderDeviceVector;
  for (uint32_t i = 0; i < numSenders; i++)
    {
      Ptr<SimpleWirelessNetDevice> senderDevice = CreateObject<SimpleWirelessNetDevice> ();
      senderDevice->SetChannel (channel);
      senderDevice->SetNode (sendingNodes.Get (i));
      senderDevice->SetAddress (Mac48Address::Allocate ());
      senderDevice->SetDataRate (dataRate);
      senderDevice->SetNoisePower (noisePower);
      queue = CreateObject<DropTailQueue<Packet>> ();
      queue->SetMaxSize (QueueSize (QueueSizeUnit::PACKETS, 100));
      senderDevice->SetQueue (queue);
      senderDevice->SetAttribute ("SlottedAloha", BooleanValue (true));
      senderDevice->TraceConnectWithoutContext ("PhyTxBegin", MakeCallback (&TransmitTrace));
      sendingNodes.Get (i)->AddDevice (senderDevice);
      senderDeviceVector.push_back (senderDevice);
      devices.Add (senderDevice);
    }

  PacketSocketHelper packetSocket;
  packetSocket.Install (nodes);

  std::vector<Ptr<PacketSocketClient> > socketVector;
  for (uint32_t i = 0; i < numSenders; i++)
    {
      PacketSocketAddress socketAddr;
      socketAddr.SetSingleDevice (senderDeviceVector[i]->GetIfIndex ());
      socketAddr.SetPhysicalAddress (receiverAddress);
      socketAddr.SetProtocol (1);
      Ptr<PacketSocketClient> client = CreateObject<PacketSocketClient> ();
      client->SetRemote (socketAddr);
      client->SetAttribute ("OnDemand", BooleanValue (true));
      client->SetAttribute ("PacketSize", UintegerValue (packetSize));
      sendingNodes.Get (i)->AddApplication (client);
      socketVector.push_back (client);
    }

  PacketSocketAddress socketAddr;
  socketAddr.SetSingleDevice (receiverDevice->GetIfIndex ());
  socketAddr.SetProtocol (1);
  Ptr<PacketSocketServer> server = CreateObject<PacketSocketServer> ();
  server->SetLocal (socketAddr);
  nodes.Get (0)->AddApplication (server);

  Simulator::Schedule (Seconds (0), &PoissonArrivalProcess, ranVar);
  Simulator::Schedule (slotTime, &SlotArrivalProcess, slotTime, 0, socketVector, backoffVar); 

  if (verbose)
    {
      Simulator::Schedule (reportingInterval, &ReportProgress, reportingInterval);
    }
  Simulator::Run ();

  uint32_t slots = Simulator::Now () / MicroSeconds (100) - 1;
  if (g_numPacketsReceived == g_maxPackets)
    {
      std::cout << "Simulation completed (successfully received " << g_numPacketsReceived << " by time "<< Simulator::Now ().GetSeconds () << "s)"<< std::endl;
      std::cout << "New packet arrival rate (packets/slot): " << lambda << std::endl;
      std::cout << "Simulation number of slot times: " << slots << std::endl;
      std::cout << "Total number of packets sent (inc. retransmissions): " << g_numPacketsSent << std::endl;
      std::cout << "Total number of packets received: " << g_numPacketsReceived << std::endl;
      std::cout << "Throughput (number received/duration): " << static_cast<double> (g_numPacketsReceived) / slots << std::endl;
    }
  else
    {
      std::cout << "Simulation terminated due to instability at time "<< Simulator::Now ().GetSeconds () << "s); try lowering lambda"<< std::endl;
    }
  
  Simulator::Destroy ();
  return 0;
}
