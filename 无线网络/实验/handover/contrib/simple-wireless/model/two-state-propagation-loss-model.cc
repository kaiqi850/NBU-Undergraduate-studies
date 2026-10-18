/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2018 University of Washington
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
 */

#include "two-state-propagation-loss-model.h"
#include "ns3/log.h"
#include "ns3/simulator.h"
#include "ns3/mobility-model.h"
#include "ns3/double.h"
#include "ns3/pointer.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("TwoStatePropagationLossModel");

// ------------------------------------------------------------------------- //

NS_OBJECT_ENSURE_REGISTERED (TwoStatePropagationLossModel);

TypeId
TwoStatePropagationLossModel::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::TwoStatePropagationLossModel")
    .SetParent<PropagationLossModel> ()
    .SetGroupName ("Propagation")
    .AddConstructor<TwoStatePropagationLossModel> ()
    .AddAttribute ("PerG",
                   "Packet Error Ratio in good state",
                   DoubleValue (0.001),
                   MakeDoubleAccessor (&TwoStatePropagationLossModel::SetPerG,
                                       &TwoStatePropagationLossModel::GetPerG),
                   MakeDoubleChecker<double> (0,1))
    .AddAttribute ("PerB",
                   "Packet Error Ratio in bad state",
                   DoubleValue (0.01),
                   MakeDoubleAccessor (&TwoStatePropagationLossModel::SetPerB,
                                       &TwoStatePropagationLossModel::GetPerB),
                   MakeDoubleChecker<double> (0,1))
    .AddAttribute ("GammaG",
                   "Gamma (exponential mean time) in good state",
                   TimeValue (Seconds (10)),
                   MakeTimeAccessor (&TwoStatePropagationLossModel::SetGammaG,
                                     &TwoStatePropagationLossModel::GetGammaG),
                   MakeTimeChecker ())
    .AddAttribute ("GammaB",
                   "Gamma (exponential mean time) in bad state",
                   TimeValue (Seconds (10)),
                   MakeTimeAccessor (&TwoStatePropagationLossModel::SetGammaB,
                                     &TwoStatePropagationLossModel::GetGammaB),
                   MakeTimeChecker ())
  ;
  return tid;
}

TwoStatePropagationLossModel::TwoStatePropagationLossModel ()
{
  NS_LOG_FUNCTION (this);
  m_ranVarGoodDuration = CreateObject<ExponentialRandomVariable> ();
  m_ranVarBadDuration = CreateObject<ExponentialRandomVariable> ();
  m_ranVarPerGood = CreateObject<UniformRandomVariable> ();
  m_ranVarPerBad = CreateObject<UniformRandomVariable> ();

  Simulator::Schedule (TimeStep (1), &TwoStatePropagationLossModel::Start, this); 
}

void
TwoStatePropagationLossModel::SetPerG (double per)
{
  m_perGood = per;
}

double
TwoStatePropagationLossModel::GetPerG (void) const
{
  return m_perGood;
}

void
TwoStatePropagationLossModel::SetPerB (double per)
{
  m_perBad = per;
}

double
TwoStatePropagationLossModel::GetPerB (void) const
{
  return m_perBad;
}

void
TwoStatePropagationLossModel::SetGammaG (Time t)
{
  m_ranVarGoodDuration->SetAttribute ("Mean", DoubleValue (t.GetSeconds ()));
}

Time
TwoStatePropagationLossModel::GetGammaG (void) const
{
  return Seconds (m_ranVarGoodDuration->GetMean ());
}

void
TwoStatePropagationLossModel::SetGammaB (Time t)
{
  m_ranVarBadDuration->SetAttribute ("Mean", DoubleValue (t.GetSeconds ()));
}

Time
TwoStatePropagationLossModel::GetGammaB (void) const
{
  return Seconds (m_ranVarBadDuration->GetMean ());
}

void
TwoStatePropagationLossModel::Start (void)
{
  NS_LOG_FUNCTION (this);
  m_goodState = true;
  double nextTime = m_ranVarGoodDuration->GetValue ();
  NS_LOG_DEBUG ("Starting model, switch to bad state at " << nextTime << " sec");
  Simulator::Schedule (Seconds (nextTime), &TwoStatePropagationLossModel::SwitchState, this);
}

double
TwoStatePropagationLossModel::DoCalcRxPower (double txPowerDbm,
                                          Ptr<MobilityModel> a,
                                          Ptr<MobilityModel> b) const
{
  NS_LOG_FUNCTION (this << txPowerDbm);
  if (m_goodState)
    {
      if (m_ranVarPerGood->GetValue () > m_perGood)
        {
          return txPowerDbm;
        }
      else
        {
          return -1000;
        }
    }
  else
    {
      if (m_ranVarPerBad->GetValue () > m_perBad)
        {
          return txPowerDbm;
        }
      else
        {
          return -1000;
        }
    }
}

void
TwoStatePropagationLossModel::SwitchState (void)
{
  if (m_goodState)
    {
      m_goodState = false;
      double nextTime = m_ranVarBadDuration->GetValue ();
      NS_LOG_DEBUG ("Switch to bad state, switching back to good state at " << nextTime << " sec"); 
      Simulator::Schedule (Seconds (nextTime), &TwoStatePropagationLossModel::SwitchState, this);
    }
  else
    {
      m_goodState = true;
      double nextTime = m_ranVarGoodDuration->GetValue ();
      NS_LOG_DEBUG ("Switch to good state, switching back to bad state at " << nextTime << " sec"); 
      Simulator::Schedule (Seconds (nextTime), &TwoStatePropagationLossModel::SwitchState, this);
    }
}

int64_t
TwoStatePropagationLossModel::DoAssignStreams (int64_t stream)
{
  m_ranVarGoodDuration->SetStream (stream);
  m_ranVarBadDuration->SetStream (stream + 1);
  m_ranVarPerGood->SetStream (stream + 2);
  m_ranVarPerBad->SetStream (stream + 3);
  return 4;
}

// ------------------------------------------------------------------------- //

} // namespace ns3
