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

// This is a program to evaluate link performance
//
// Network topology:
//
//  Simple wireless 192.168.1.0
//
//   sender              receiver 
//    * <-- distance -->  *
//    |                   |
//    n0                  n1
//
// Users may vary the following command-line arguments in addition to the
// attributes, global values, and default values typically available:
//
// The default data rate of the link is 100 Mbps.
//
//    (to be completed)
//

#include <fstream>
#include <iostream>
#include <cmath>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/propagation-module.h"
#include "ns3/two-state-propagation-loss-model.h"
#include "ns3/simple-wireless-channel.h"
#include "ns3/simple-wireless-net-device.h"
#include "ns3/snr-per-error-model.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LinkPerformanceExample");

std::ofstream g_fileRssi;
std::ofstream g_fileSummary;
uint64_t g_numPacketsSent = 0;
uint64_t g_numPacketsReceived = 0;
uint64_t g_numPacketsDropped = 0;
uint64_t g_maxPackets = 0;

void
TransmitTrace (Ptr<const Packet> p, Mac48Address from, Mac48Address to, uint16_t proto)
{
  g_numPacketsSent++;
}

void
PhyReceiveTrace (Ptr<const Packet> p, double rxPower, Mac48Address from)
{
  g_fileRssi << Simulator::Now ().GetSeconds () << " " << rxPower << std::endl;
}

void
MacReceiveTrace (Ptr<const Packet> p)
{
  g_numPacketsReceived++;
  if (g_numPacketsSent == g_maxPackets)
    {
      Simulator::Stop ();
    }
}

void
DropTrace (Ptr<const Packet> p, double rxPower, Mac48Address from)
{
  g_numPacketsDropped++;
  if (g_numPacketsSent == g_maxPackets)
    {
      Simulator::Stop ();
    }
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

int
main (int argc, char *argv[])
{
  DataRate dataRate = DataRate ("100Mbps");
  double distance = 25.0; // meters
  uint32_t packetSize = 1024;
  double noisePower = -100; // dbm
  double transmitPower = 16; // dbm
  double frequency = 5000000000; // Hz
  std::string lossModelType = "Friis";
  std::string metadata = "";

  g_numPacketsSent = 0;
  g_numPacketsReceived = 0;
  g_numPacketsDropped = 0;
  g_maxPackets = 1000;

  CommandLine cmd;
  cmd.AddValue("distance","the distance between the two nodes",distance);
  cmd.AddValue("maxPackets","the number of packets to send",g_maxPackets);
  cmd.AddValue("packetSize","packet size in bytes",packetSize);
  cmd.AddValue("transmitPower","transmit power in dBm",transmitPower);
  cmd.AddValue("noisePower","noise power in dBm",noisePower);
  cmd.AddValue("frequency","frequency in Hz",frequency);
  cmd.AddValue("lossModelType","loss model (Friis, LogDistance, or TwoState)",lossModelType);
  cmd.AddValue("metadata","metadata about experiment run",metadata);
  cmd.Parse (argc, argv);

  g_fileRssi.open ("link-performance-rssi.dat", std::ofstream::out);
  g_fileSummary.open ("link-performance-summary.dat", std::ofstream::app);
  
  Ptr<Node> senderNode = CreateObject<Node> ();
  Ptr<Node> receiverNode = CreateObject<Node> ();
  NodeContainer nodes;
  nodes.Add (senderNode);
  nodes.Add (receiverNode);

  MobilityHelper mobility;
  Ptr<ListPositionAllocator> positionAllocator = CreateObject<ListPositionAllocator> ();
  positionAllocator->Add (Vector (0.0, 0.0, 0.0));
  positionAllocator->Add (Vector (distance, 0.0, 0.0));
  mobility.SetPositionAllocator (positionAllocator);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (nodes);

  Ptr<SimpleWirelessChannel> channel = CreateObject<SimpleWirelessChannel> ();
  if (lossModelType == "Friis")
    {    
      Ptr<FriisPropagationLossModel> lossModel = CreateObject<FriisPropagationLossModel> ();
      lossModel->SetFrequency (frequency);
      channel->AddPropagationLossModel (lossModel);
    }
  else if (lossModelType == "LogDistance")
    {
      Ptr<LogDistancePropagationLossModel> lossModel = CreateObject<LogDistancePropagationLossModel> ();
      channel->AddPropagationLossModel (lossModel);
    }
  else if (lossModelType == "TwoState")
    {
      Ptr<TwoStatePropagationLossModel> lossModel = CreateObject<TwoStatePropagationLossModel> ();
      channel->AddPropagationLossModel (lossModel);
    }
  else
    {
      std::cerr << "Error, loss model " << lossModelType << " is unknown " << std::endl;
      exit (1);
    }

  NetDeviceContainer devices;
  Ptr<SimpleWirelessNetDevice> senderDevice = CreateObject<SimpleWirelessNetDevice> ();
  senderDevice->SetChannel (channel);
  senderDevice->SetNode (senderNode);
  senderDevice->SetAddress (Mac48Address::Allocate ());
  senderDevice->SetDataRate (dataRate);
  senderDevice->SetAttribute ("TxPower", DoubleValue (transmitPower));
  senderDevice->SetNoisePower (noisePower);
  senderDevice->TraceConnectWithoutContext ("PhyTxBegin", MakeCallback (&TransmitTrace));
  senderNode->AddDevice (senderDevice);
  devices.Add (senderDevice);
  Ptr<SimpleWirelessNetDevice> receiverDevice = CreateObject<SimpleWirelessNetDevice> ();
  receiverDevice->SetChannel (channel);
  receiverDevice->SetNode (receiverNode);
  receiverDevice->SetAddress (Mac48Address::Allocate ());
  receiverDevice->SetDataRate (dataRate);
  receiverDevice->SetNoisePower (noisePower);
  receiverDevice->TraceConnectWithoutContext ("PhyRxEnd", MakeCallback (&PhyReceiveTrace));
  receiverDevice->TraceConnectWithoutContext ("MacRx", MakeCallback (&MacReceiveTrace));
  receiverDevice->TraceConnectWithoutContext ("PhyRxDrop", MakeCallback (&DropTrace));
  Ptr<BpskSnrPerErrorModel> errorModel = CreateObject<BpskSnrPerErrorModel> ();
  receiverDevice->SetSnrPerErrorModel (errorModel);
  receiverNode->AddDevice (receiverDevice);
  devices.Add (receiverDevice);

  // Packet sockets bypass the IP layer and read and write directly from
  // the SimpleWireless devices
  PacketSocketHelper packetSocket;
  packetSocket.Install (nodes);

  PacketSocketAddress socketAddr;
  socketAddr.SetSingleDevice (senderDevice->GetIfIndex ());
  socketAddr.SetPhysicalAddress (receiverDevice->GetAddress ());
  socketAddr.SetProtocol (1);

  OnOffHelper onoff ("ns3::PacketSocketFactory", Address (socketAddr));
  onoff.SetConstantRate (DataRate (81920)); // 1024 bytes every 100 ms
  onoff.SetAttribute ("PacketSize", UintegerValue (packetSize));
  onoff.SetAttribute ("MaxBytes", UintegerValue (g_maxPackets * packetSize));

  ApplicationContainer apps = onoff.Install (nodes.Get (0));
  apps.Start (Seconds (1.0));

  // Setup receiver
  TypeId tid = TypeId::LookupByName ("ns3::PacketSocketFactory");
  Ptr<Socket> sink = Socket::CreateSocket (nodes.Get (1), tid);
  sink->Bind ();
  sink->SetRecvCallback (MakeCallback (&ReceivePacket));

  Simulator::Run ();

  double per = static_cast<double> (g_numPacketsDropped) / g_numPacketsSent;
  double error = 0;
  if (per > 0 && per < 1)
    {
      // error bars for 95% confidence interval of a binomial distribution
      // per +/- z * sqrt (per * (1-p)/n). Here, z = 1.96
      error = 1.96 * sqrt (per * (1 - per)/g_numPacketsSent);
    }
  std::cout << "sent " << g_numPacketsSent
            << " rcv " << g_numPacketsReceived
            << " drop " << g_numPacketsDropped
            << " per " << per
            << " error " << error << std::endl;
  g_fileSummary << g_numPacketsSent << " " << g_numPacketsReceived << " " 
                << g_numPacketsDropped << " " << per << " "
                << error << " " << metadata << std::endl;
  
  Simulator::Destroy ();
  g_fileRssi.close ();
  g_fileSummary.close ();
  return 0;
}
