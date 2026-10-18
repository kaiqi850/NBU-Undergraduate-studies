/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2005,2006,2007 INRIA
 * Copyright (c) 2019 University of Washington
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
 *
 * Author: Mathieu Lacage <mathieu.lacage@sophia.inria.fr>
 * Original wifi-ap.cc modified for DCF experimentation by Tom Henderson
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/wifi-module.h"
#include "ns3/propagation-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/netanim-module.h"
#include <iostream>
#include <iomanip>
#include <fstream>

using namespace ns3;

// Define global variables
std::ofstream g_fileApRx;
std::ofstream g_fileStaTx;
std::ofstream g_fileRxOk;
std::ofstream g_fileRxError;
std::ofstream g_filePhyTx;
std::ofstream g_fileState;

// Define a packet counter, to assist in receive throughput
uint64_t g_packetCount;

// Parse context strings of the form "/NodeList/3/DeviceList/1/Mac/Assoc"
// to extract the NodeId
uint32_t
ContextToNodeId (std::string context)
{
  std::string sub = context.substr (10);  // skip "/NodeList/"
  uint32_t pos = sub.find ("/Device");
  return atoi (sub.substr (0,pos).c_str ());
}

void
StaTxTrace (std::string context, Ptr<const Packet> p)
{
  g_fileStaTx << Simulator::Now ().GetSeconds () << " " << ContextToNodeId (context) << " " << p->GetSize () << std::endl;
}

bool
ApRxTrace (Ptr<NetDevice> device, Ptr<const Packet> p, uint16_t protocol, const Address &from)
{
  g_fileApRx << Simulator::Now ().GetSeconds () << " 0 " << Mac48Address::ConvertFrom (from) << " " << p->GetSize () << std::endl;
  g_packetCount++;
  return true;
}

void
PhyRxOkTrace (std::string context, Ptr<const Packet> packet, double snr, WifiMode mode, WifiPreamble preamble)
{
  g_fileRxOk << Simulator::Now ().GetSeconds () << " " << ContextToNodeId (context) << " size: " << packet->GetSize () << " snr (dB): " << 10.0 * std::log10 (snr) << std::endl;
}

void
PhyRxErrorTrace (std::string context, Ptr<const Packet> packet, double snr)
{
  g_fileRxError << Simulator::Now ().GetSeconds () << " " << ContextToNodeId (context) << " size: " << packet->GetSize () << " snr (dB): " << 10.0 * std::log10 (snr) << std::endl;
}

void
PhyTxTrace (std::string context, Ptr<const Packet> packet, WifiMode mode, WifiPreamble preamble, uint8_t txPower)
{
  g_filePhyTx << Simulator::Now ().GetSeconds () << " " << ContextToNodeId (context) << " size: " << packet->GetSize () << " txPower: " << static_cast<uint16_t> (txPower) << std::endl;
}

void
PhyStateTrace (std::string context, Time start, Time duration, WifiPhyState state)
{
  if (state != WifiPhyState::CCA_BUSY)
    {
      g_fileState << Simulator::Now ().GetSeconds () << " " << ContextToNodeId (context) << " state: " << state << " start: " << std::fixed << std::setprecision (6) << start.GetSeconds () << " duration " << duration.GetSeconds () << std::endl;
    }
}

int main (int argc, char *argv[])
{
  bool ascii = false;
  bool pcap = false;
  bool animate = false;
  uint32_t numStas = 1;
  uint32_t radius = 25; // m
  uint32_t rtsThreshold = 2200;
  uint32_t packetSize = 1900;
  uint32_t cwMin = 15;
  uint32_t cwMax = 1023;
  double duration = 10; // seconds; simulation will run for 'duration + 1'
  double packetArrivalRate = 1; // 1 per second
  std::string fileNameApRx = "wifi-dcf-ap-rx-trace.dat";
  std::string fileNameStaTx = "wifi-dcf-sta-tx-trace.dat";
  std::string fileNameRxOk = "wifi-dcf-rx-ok-trace.dat";
  std::string fileNameRxError = "wifi-dcf-rx-error-trace.dat";
  std::string fileNamePhyTx = "wifi-dcf-phy-tx.dat";
  std::string fileNameState = "wifi-dcf-state-trace.dat";

  CommandLine cmd;
  cmd.AddValue ("ascii", "Print ascii trace information if true", ascii);
  cmd.AddValue ("pcap", "Print pcap trace information if true", pcap);
  cmd.AddValue ("animate", "Print animation trace if true", animate);
  cmd.AddValue ("packetSize", "Set packet size (bytes)", packetSize);
  cmd.AddValue ("packetArrivalRate", "Packet arrival rate per second", packetArrivalRate);
  cmd.AddValue ("numStas", "Number of STA devices", numStas);
  cmd.AddValue ("cwMin", "CwMin parameter of DCF", cwMin);
  cmd.AddValue ("cwMax", "CwMax parameter of DCF", cwMax);
  cmd.AddValue ("duration", "Duration of data logging phase (s)", duration);
  cmd.AddValue ("radius", "Radius for node dropping around AP (m)", radius);
  cmd.AddValue ("rtsThreshold", "Packet size threshold for RTS (bytes)", rtsThreshold);
  cmd.Parse (argc, argv);

  g_fileApRx.open (fileNameApRx.c_str(), std::ofstream::out);
  g_fileStaTx.open (fileNameStaTx.c_str(), std::ofstream::out);
  g_fileRxOk.open (fileNameRxOk.c_str(), std::ofstream::out);
  g_fileRxError.open (fileNameRxError.c_str(), std::ofstream::out);
  g_filePhyTx.open (fileNamePhyTx.c_str(), std::ofstream::out);
  g_fileState.open (fileNameState.c_str(), std::ofstream::out);

  g_packetCount = 0;

  Packet::EnablePrinting ();

  NodeContainer ap;
  NodeContainer stas;

  // Create the nodes
  ap.Create (1);
  stas.Create (numStas);

  // Create a single-model spectrum channel
  Ptr<SingleModelSpectrumChannel> spectrumChannel = CreateObject<SingleModelSpectrumChannel> ();
  Ptr<FriisPropagationLossModel> lossModel = CreateObject<FriisPropagationLossModel> ();
  spectrumChannel->AddPropagationLossModel (lossModel);
  Ptr<ConstantSpeedPropagationDelayModel> delayModel = CreateObject<ConstantSpeedPropagationDelayModel> ();
  spectrumChannel->SetPropagationDelayModel (delayModel);

  // Create a helper to install a WifiPhy matched to the spectrum channel
  SpectrumWifiPhyHelper wifiPhy = SpectrumWifiPhyHelper::Default ();
  wifiPhy.SetChannel (spectrumChannel);

  wifiPhy.SetErrorRateModel ("ns3::YansErrorRateModel"); // classical model
  wifiPhy.Set ("Frequency", UintegerValue (5180)); // channel 36 at 20 MHz
  wifiPhy.Set ("TxPowerStart", DoubleValue (16));  // 40 mW at 5 GHz
  wifiPhy.Set ("TxPowerEnd", DoubleValue (16));    // 40 mW dBm

  // Configure the MAC layer
  WifiHelper wifi;
  WifiMacHelper wifiMac;
  Ssid ssid = Ssid ("wifi-dcf");
  wifi.SetStandard (WIFI_PHY_STANDARD_80211a);
  //wifi.SetRemoteStationManager ("ns3::MinstrelWifiManager");
  wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager", 
                                "DataMode", StringValue ("OfdmRate54Mbps"),
                                "ControlMode", StringValue ("OfdmRate24Mbps"),
                                "RtsCtsThreshold", UintegerValue (rtsThreshold));
  // Create the NetDevices
  NetDeviceContainer apDev;
  NetDeviceContainer staDevs;
  // setup STAs
  wifiMac.SetType ("ns3::StaWifiMac",
                   "Ssid", SsidValue (ssid));
  staDevs = wifi.Install (wifiPhy, wifiMac, stas);
  // setup AP
  wifiMac.SetType ("ns3::ApWifiMac",
                   "Ssid", SsidValue (ssid));
  apDev =  wifi.Install (wifiPhy, wifiMac, ap);

  // Some Wi-Fi attributes must be set at post-construction time when
  // SetStandard() is used; MinCw and MaxCw are two such attributes
  Config::Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/$ns3::RegularWifiMac/Txop/MinCw", UintegerValue (cwMin));
  Config::Set ("/NodeList/*/DeviceList/*/$ns3::WifiNetDevice/Mac/$ns3::RegularWifiMac/Txop/MaxCw", UintegerValue (cwMax));

  // The mobility model places nodes; here, within a disc of a given radius
  MobilityHelper mobility;
  Ptr<UniformDiscPositionAllocator> positionAllocator = CreateObject<UniformDiscPositionAllocator> ();
  positionAllocator->SetRho (radius);
  mobility.SetPositionAllocator (positionAllocator);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (stas);
  // Place the AP at the center position
  Ptr<ListPositionAllocator> apPositionAllocator = CreateObject<ListPositionAllocator> ();
  apPositionAllocator->Add (Vector (0.0, 0.0, 0.0));
  mobility.SetPositionAllocator (apPositionAllocator);
  mobility.Install (ap);

  // Enable packet sockets to couple to the traffic generator
  PacketSocketHelper packetSocket;
  packetSocket.Install (stas);
  packetSocket.Install (ap);

  // Install traffic generation in all STAs
  PacketSocketAddress socket;
  // Create a random variable to introduce jitter in the start times for
  // the traffic generators
  Ptr<UniformRandomVariable> startTimeVariable = CreateObject<UniformRandomVariable> ();
  startTimeVariable->SetAttribute ("Max", DoubleValue (0.1));
  // Convert packet arrival rate (packets per second) to a data rate in bps
  uint64_t bps = static_cast<uint64_t> (packetArrivalRate * packetSize * 8);
  for (uint32_t i = 0; i < staDevs.GetN (); i++)
    {
      socket.SetSingleDevice (staDevs.Get (i)->GetIfIndex ());
      socket.SetPhysicalAddress (apDev.Get (0)->GetAddress ());
      socket.SetProtocol (1);
      OnOffHelper onoff ("ns3::PacketSocketFactory", Address (socket));
      onoff.SetConstantRate (DataRate (bps), packetSize);

      ApplicationContainer apps = onoff.Install (stas.Get (i));
      apps.StartWithJitter (Seconds (1.0), startTimeVariable);
      // Account for up to 100 ms of jitter in the start time
      apps.Stop (Seconds (duration + 1) + MilliSeconds (100));
    }

  // Account for up to 100 ms of jitter in the app start times
  Simulator::Stop (Seconds (duration + 1) + MilliSeconds (100));

  // Set traces
  Ptr<WifiNetDevice> apNetDevice = DynamicCast<WifiNetDevice> (apDev.Get (0));
  apNetDevice->SetReceiveCallback (MakeCallback (&ApRxTrace));
  Config::Connect ("/NodeList/*/DeviceList/*/Mac/MacTx", MakeCallback (&StaTxTrace));
  Config::Connect ("/NodeList/0/DeviceList/*/Phy/State/RxOk", MakeCallback (&PhyRxOkTrace));
  Config::Connect ("/NodeList/0/DeviceList/*/Phy/State/RxError", MakeCallback (&PhyRxErrorTrace));
  Config::Connect ("/NodeList/*/DeviceList/*/Phy/State/Tx", MakeCallback (&PhyTxTrace));
  Config::Connect ("/NodeList/*/DeviceList/*/Phy/State/State", MakeCallback (&PhyStateTrace));

  if (animate)
    {
      AnimationInterface anim ("wifi-dcf-animation.xml");
      anim.UpdateNodeDescription (ap.Get (0), "AP");
      anim.UpdateNodeColor (ap.Get (0), 0, 255, 0);
      for (uint32_t i = 0; i < stas.GetN (); ++i)
        {
          anim.UpdateNodeDescription (stas.Get (i), "STA");
          anim.UpdateNodeColor (stas.Get (i), 255, 0, 0);
        }
     anim.EnablePacketMetadata ();
    }

  if (ascii)
    {
      AsciiTraceHelper asciiTraceHelper;
      Ptr<OutputStreamWrapper> stream = asciiTraceHelper.CreateFileStream ("wifi-dcf.tr");
      wifiPhy.EnableAsciiAll (stream);
    }

  if (pcap)
    {
      wifiPhy.EnablePcap ("wifi-dcf", apDev.Get (0));
    }

  Simulator::Run ();

  std::cout << "Throughput observed at AP: " << ((g_packetCount * packetSize * 8)/duration)/1e6 << " Mb/s" << std::endl;

  Simulator::Destroy ();

  g_fileApRx.close ();
  g_fileStaTx.close ();
  g_fileRxOk.close ();
  g_fileRxError.close ();
  g_filePhyTx.close ();
  g_fileState.close ();
  return 0;
}
